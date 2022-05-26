terrain_fragment_shader = """
#version 150

// This is the terrain fragment shader. There is a lot of code in here
// which is not necessary to render the terrain, but included for convenience -
// Like generating normals from the heightmap or a simple fog effect.

// Most of the time you want to adjust this shader to get your terrain the look
// you want. The vertex shader most likely will stay the same.

in vec2 terrain_uv;
in vec3 vtx_pos;
out vec4 color;

uniform struct {
  sampler2D data_texture;
  sampler2D heightfield;
  int view_index;
  int terrain_size;
  int chunk_size;
} ShaderTerrainMesh;

uniform sampler2D p3d_Texture0;
uniform vec3 wspos_camera;

// Compute normal from the heightmap, this assumes the terrain is facing z-up
vec3 get_terrain_normal() {
  const float terrain_height = 128.0;
  vec3 pixel_size = vec3(1.0, -1.0, 0) / textureSize(ShaderTerrainMesh.heightfield, 0).xxx;
  float u0 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.yz).x * terrain_height;
  float u1 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.xz).x * terrain_height;
  float v0 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.zy).x * terrain_height;
  float v1 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.zx).x * terrain_height;
  vec3 tangent = normalize(vec3(1.0, 0, u1 - u0));
  vec3 binormal = normalize(vec3(0, 1.0, v1 - v0));
  return normalize(cross(tangent, binormal));
}

void main() {
  vec3 diffuse = texture(p3d_Texture0, terrain_uv).xyz;
  vec3 normal = get_terrain_normal();

  vec3 fake_sun = normalize(vec3(0.7, 0.2, 0.6));
  vec3 shading = max(0.0, dot(normal, fake_sun)) * diffuse;
  shading += vec3(0.07, 0.07, 0.1);
  color = vec4(shading, 1);
}
"""

terrain_vertex_shader = """
#version 150

// This is the default terrain vertex shader. Most of the time you can just copy
// this and reuse it, and just modify the fragment shader.

in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

uniform struct {
  sampler2D data_texture;
  sampler2D heightfield;
  int view_index;
  int terrain_size;
  int chunk_size;
} ShaderTerrainMesh;

out vec2 terrain_uv;
out vec3 vtx_pos;

void main() {

  // Terrain data has the layout:
  // x: x-pos, y: y-pos, z: size, w: clod
  vec4 terrain_data = texelFetch(ShaderTerrainMesh.data_texture,
    ivec2(gl_InstanceID, ShaderTerrainMesh.view_index), 0);

  vec3 chunk_position = p3d_Vertex.xyz;

  // CLOD implementation
  float clod_factor = smoothstep(0, 1, terrain_data.w);
  chunk_position.xy -= clod_factor * fract(chunk_position.xy * ShaderTerrainMesh.chunk_size / 2.0)
                          * 2.0 / ShaderTerrainMesh.chunk_size;

  // Scale the chunk
  chunk_position *= terrain_data.z * float(ShaderTerrainMesh.chunk_size)
                    / float(ShaderTerrainMesh.terrain_size);
  chunk_position.z *= ShaderTerrainMesh.chunk_size;

  // Offset the chunk, it is important that this happens after the scale
  chunk_position.xy += terrain_data.xy / float(ShaderTerrainMesh.terrain_size);

  // Compute the terrain UV coordinates
  terrain_uv = chunk_position.xy;

  // Sample the heightfield and offset the terrain - we do not need to multiply
  // the height with anything since the terrain transform is included in the
  // model view projection matrix.
  chunk_position.z += texture(ShaderTerrainMesh.heightfield, terrain_uv).x;
  gl_Position = p3d_ModelViewProjectionMatrix * vec4(chunk_position, 1);

  // Output the vertex world space position - in this case we use this to render
  // the fog.
  vtx_pos = (p3d_ModelMatrix * vec4(chunk_position, 1)).xyz;
}
"""

import os
from panda3d.core import NodePath
from panda3d.core import ShaderTerrainMesh
from panda3d.core import Shader
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import ZUp


def make_terrain(filename, height):
    base_filename = os.path.splitext('./'+filename)[0]
    img_name = '{}.png'.format(base_filename)
    img = loader.load_texture(img_name)
    width = img.get_x_size()
    offset = width/2.0 - 0.5
    terrain = ShaderTerrainMesh()
    terrain.set_heightfield(img)
    terrain.set_target_triangle_width(20)
    terrain.set_update_enabled(True)
    terrain.set_chunk_size(32)
    terrain_root = NodePath(terrain)
    terrain_shader = Shader.make(Shader.SL_GLSL, vertex=terrain_vertex_shader, fragment=terrain_fragment_shader)
    terrain_root.set_shader(terrain_shader)
    terrain_root.set_shader_input("camera", base.cam)
    terrain_root.set_scale(1024,1024,height)
    terrain_root.set_pos(-offset, -offset, -height/2)
    terrain.generate()
    shape = BulletHeightfieldShape(img, height, ZUp)
    node = BulletRigidBodyNode(base_filename)
    node.add_shape(shape)
    terrain_root.attach_new_node(node)
    return terrain_root
