// Three.js camera, geometry, clay/depth/normal and edge passes adapted from the courtyard pilot.
import * as T from 'three';
const world = ([east,up,north]) => new T.Vector3(east,up,-north);
function requireValue(ok,message) { if (!ok) throw Error(message); }
function text(s) {return typeof s === 'string' && s.trim().length > 0;}
function vec(v) { return Array.isArray(v) && v.length === 3 && v.every(Number.isFinite); }
function color(s) { requireValue(/^#[0-9a-fA-F]{6}$/.test(s),'Expected #RRGGBB'); return new T.Color(s); }
function makePart(p) {
  let geom;
  if (p.kind === 'box') {
    requireValue(vec(p.size) && p.size.every(n=>n>0),'Box needs positive size');
    geom = new T.BoxGeometry(...p.size);
  } else if (p.kind === 'cylinder') {
    requireValue([p.radius_top,p.radius_bottom,p.height].every(Number.isFinite) && p.height>0
      && Math.min(p.radius_top,p.radius_bottom)>=0 && Math.max(p.radius_top,p.radius_bottom)>0,'Invalid cylinder');
    geom = new T.CylinderGeometry(p.radius_top,p.radius_bottom,p.height,20);
  } else if (p.kind === 'tube') {
    requireValue(p.points?.length>=2 && p.points.every(vec) && Number.isFinite(p.radius) && p.radius>0,'Invalid tube');
    const curve = new T.CurvePath();
    p.points.slice(1).forEach((v,i)=>curve.add(new T.LineCurve3(world(p.points[i]),world(v))));
    geom = new T.TubeGeometry(curve, Math.max(32,p.points.length*8),p.radius,8,false);
  } else if (p.kind === 'mesh') {
    requireValue(p.vertices?.length>=3 && p.vertices.every(vec) && p.faces?.length && p.faces.every(f=>Array.isArray(f) && f.length===3 && f.every(i=>Number.isInteger(i)&&i>=0&&i<p.vertices.length)),'Invalid mesh');
    geom = new T.BufferGeometry();
    geom.setAttribute('position',new T.Float32BufferAttribute(p.vertices.flatMap(v=>world(v).toArray()),3));
    geom.setIndex(p.faces.flatMap(([a,b,c])=>[a,c,b]));
    geom.computeVertexNormals();
  } else throw Error('Unknown geometry: '+p.kind);
  requireValue(vec(p.center) && (p.yaw_deg===undefined || Number.isFinite(p.yaw_deg)),'Each part needs center and optional numeric yaw');
  geom.rotateY(T.MathUtils.degToRad(p.yaw_deg || 0));
  geom.translate(...world(p.center).toArray());
  return geom;
}
function idMaterial(code) {
  const channels=[code>>16,(code>>8)&255,code&255].map(v=>v/255);
  return new T.ShaderMaterial({side:T.DoubleSide, uniforms:{idColor:{value:new T.Vector3(...channels)}},
    vertexShader:'void main(){gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader:'uniform vec3 idColor;void main(){gl_FragColor=vec4(idColor,1.0);}'});
}
function setMaterials(meshes,field){for(const m of meshes) m.material=m.userData[field];}
function bytesToCode(bytes,i) {return (bytes[i]<<16)|(bytes[i+1]<<8)|bytes[i+2];}
export async function render(data,camID,stateID) {
  const c=data.cameras?.find(x=>x.id===camID), s=data.states?.find(x=>x.id===stateID);
  requireValue(text(data.place_entity_id)&&text(data.blockout_version)&&c&&s,'Missing place, blockout version, camera or state');
  requireValue(data.cameras.filter(x=>x.id===camID).length===1 && data.states.filter(x=>x.id===stateID).length===1,'Duplicate camera/state');
  requireValue(text(c.source)&&text(s.source)&&vec(c.pos)&&vec(c.target)&&world(c.pos).distanceTo(world(c.target))>0,'Missing camera/state evidence or invalid camera');
  const [w,h]=c.resolution;
  requireValue([w,h].every(n=>Number.isInteger(n)&&n>0)&&c.vfov>0&&c.vfov<179&&c.near>0&&c.far>c.near,'Invalid frustum or resolution');
  const cam = new T.PerspectiveCamera(c.vfov,w/h,c.near,c.far);
  cam.position.copy(world(c.pos)); cam.lookAt(world(c.target)); cam.updateMatrixWorld();
  const entities=data.entities;
  requireValue(entities?.length>0 && entities.length<0xffffff && new Set(entities.map(e=>e.entity_id)).size===entities.length,'Empty or duplicate entities');
  requireValue(entities.some(e=>e.entity_id===data.place_entity_id),'Missing place entity');
  const scene=new T.Scene(), meshes=[], rows=[], box=new T.Box3();
  const projection=new T.Matrix4().multiplyMatrices(cam.projectionMatrix,cam.matrixWorldInverse);
  const frustum=new T.Frustum().setFromProjectionMatrix(projection);
  const depth=new T.ShaderMaterial({side:T.DoubleSide,uniforms:{near:{value:c.near},far:{value:c.far}},
    vertexShader:'varying float d;void main(){vec4 mv=modelViewMatrix*vec4(position,1.);d=-mv.z;gl_Position=projectionMatrix*mv;}',
    fragmentShader:'varying float d;uniform float near,far;void main(){float v=1.-clamp((d-near)/(far-near),0.,1.);gl_FragColor=vec4(vec3(v),1.);}' });
  const normal=new T.MeshNormalMaterial({side:T.DoubleSide});
  const white=new T.MeshBasicMaterial({color:0xffffff,side:T.DoubleSide,polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1});
  const edgeLines=[];
  for(const [i,e] of [...entities].sort((a,b)=>a.entity_id.localeCompare(b.entity_id)).entries()) {
    requireValue(text(e.entity_id) && e.design_version!=null && String(e.design_version).trim() && text(e.source) && text(e.design_path) && Array.isArray(e.parts),'Missing entity identity/design evidence/parts');
    const code=((i+1)*0x9e3779)%0x1000000;
    const row={entity_id:e.entity_id,design_version:e.design_version,source:e.source,design_path:e.design_path,
      color:'#'+code.toString(16).padStart(6,'0'), visible_px:0,unoccluded_projection_px:0,occluded_by:{},in_frustum_bounds:false};
    rows.push(row);
    const labels=new Set();
    for(const p of e.parts) {
      requireValue(text(p.id)&&!labels.has(p.id)&&text(p.material),'Missing or duplicate part ID/material zone');
      labels.add(p.id);
      if(p.states && !p.states.includes(stateID))continue;
      const material=s.materials?.[p.material];
      requireValue(material && text(material.surface) && [material.roughness ?? 1,material.metalness ?? 0].every(n=>Number.isFinite(n)&&n>=0&&n<=1),'Missing or invalid material zone in state: '+p.material);
      const mesh=new T.Mesh(makePart(p));
      mesh.userData={row,code,plan:p.plan!==false,id:idMaterial(code),clay:new T.MeshStandardMaterial({color:color(material.clay),roughness:material.roughness ?? 1,metalness:material.metalness ?? 0,side:T.DoubleSide})};
      mesh.castShadow=true;mesh.receiveShadow=true;scene.add(mesh);meshes.push(mesh);
      const bounds=new T.Box3().setFromObject(mesh);
      box.union(bounds); row.in_frustum_bounds ||= frustum.intersectsBox(bounds);
      const line=new T.LineSegments(new T.EdgesGeometry(mesh.geometry,25),new T.LineBasicMaterial({color:0}));
      edgeLines.push(line);
    }
  }
  requireValue(meshes.length>0,'No geometry enabled in this state');
  const renderer=new T.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setSize(w,h,false);renderer.setPixelRatio(1);
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
  const lighting=s.light;
  requireValue(lighting && Number.isFinite(lighting.ambient) && lighting.ambient>=0 && Number.isFinite(lighting.sun) && lighting.sun>=0 && typeof lighting.shadows==='boolean' && vec(lighting.sun_direction) && world(lighting.sun_direction).lengthSq()>0,'Invalid state lighting');
  scene.background=color(lighting.sky);
  scene.add(new T.HemisphereLight(color(lighting.sky),color(lighting.ground),lighting.ambient));
  const center=box.getCenter(new T.Vector3()), extent=Math.max(box.getSize(new T.Vector3()).length(),1);
  const sun=new T.DirectionalLight(color(lighting.sun_color),lighting.sun);
  sun.target.position.copy(center);sun.position.copy(center).addScaledVector(world(lighting.sun_direction).normalize(),extent*2);
  sun.castShadow=lighting.shadows;sun.shadow.mapSize.set(2048,2048);
  Object.assign(sun.shadow.camera,{left:-extent,right:extent,top:extent,bottom:-extent,near:0.01,far:extent*4});
  sun.shadow.camera.updateProjectionMatrix();scene.add(sun,sun.target);
  const save=async(name,camera)=>{renderer.render(scene,camera);await window.savePNG(name,renderer.domElement.toDataURL('image/png'));};
  setMaterials(meshes,'clay');await save('clay',cam);
  scene.background=new T.Color(0);meshes.forEach(m=>m.material=depth);await save('depth',cam);
  scene.background=new T.Color(0x8080ff);meshes.forEach(m=>m.material=normal);await save('normal',cam);
  scene.background=new T.Color(0xffffff);meshes.forEach(m=>m.material=white);scene.add(...edgeLines);await save('line',cam);scene.remove(...edgeLines);
  scene.background=new T.Color(0);setMaterials(meshes,'id');
  await save('semantic',cam);
  const rt=new T.WebGLRenderTarget(w,h,{type:T.UnsignedByteType,colorSpace:T.NoColorSpace,samples:0});
  renderer.setRenderTarget(rt);
  const pixels=()=>{renderer.render(scene,cam);const bytes=new Uint8Array(w*h*4);renderer.readRenderTargetPixels(rt,0,0,w,h,bytes);return bytes;};
  const full=pixels(), ids=new Map(meshes.map(m=>[m.userData.code,m.userData.row.entity_id]));
  for(const row of rows) {
    const group=meshes.filter(m=>m.userData.row===row);
    if(group.length && row.in_frustum_bounds) {
      for(const m of meshes)m.visible=m.userData.row===row;
      const solo=pixels();
      let minX=w,minY=h,maxX=-1,maxY=-1;
      for(let j=0;j<solo.length;j+=4) {
        if(!bytesToCode(solo,j))continue;
        row.unoccluded_projection_px++;
        const final=ids.get(bytesToCode(full,j));
        if(final===row.entity_id) {
          row.visible_px++;const x=(j/4)%w,y=h-1-Math.floor(j/(4*w));
          minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);
        } else if(final) row.occluded_by[final]=(row.occluded_by[final]||0)+1;
      }
      if(row.visible_px)row.visible_bounds_xyxy=[minX,minY,maxX,maxY];
    }
    row.result=!group.length?'no_active_geometry':row.visible_px?'visible':row.unoccluded_projection_px?'occluded':row.in_frustum_bounds?'no_raster_sample':'outside_frustum';
  }
  renderer.setRenderTarget(null);rt.dispose();
  // Orthographic plan fits active geometry, camera and target. Helpers use true projection.
  const planBox=box.clone().expandByPoint(cam.position).expandByPoint(world(c.target));
  const focus=planBox.getCenter(new T.Vector3()),dims=planBox.getSize(new T.Vector3());
  const span=Math.max(dims.x,dims.z,1)*0.58;
  const top=new T.OrthographicCamera(-span,span,span,-span,0.01,dims.y+4*span+10);
  top.position.set(focus.x,planBox.max.y+span+2,focus.z);top.up.set(0,0,-1);top.lookAt(focus);top.updateMatrixWorld();
  for(const m of meshes)m.visible=m.userData.plan;
  const helper=new T.CameraHelper(cam);
  helper.material.depthTest=false;helper.renderOrder=1;scene.add(helper);
  renderer.setSize(Math.max(w,h),Math.max(w,h),false);await save('top',top);
  renderer.dispose();
  return {place_entity_id:data.place_entity_id,blockout_version:data.blockout_version,camera:c,state_id:s.id,state_source:s.source,entities:rows,visible_entity_ids:rows.filter(x=>x.visible_px).map(x=>x.entity_id)};
}
