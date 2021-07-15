# The obj dumped from GPA lacks texcoord, hence use this script to add texcoords
# openmesh cheatsheet https://gist.github.com/zishun/0ba4f7925a1cd1ece890eb4dee4cd81e

import openmesh
import struct

uv_float_idx = 0

def process_mesh(in_bin_filename, in_obj_filename, stride, flip_v, out_filename):
    global uv_float_idx
    uv_float_idx = 0
    uv_floats = []
    def add_uv_float(number, stride):
        global uv_float_idx
        mod_idx = uv_float_idx % int(stride/4)
        if mod_idx < 2:
            if flip_v and mod_idx == 1:
                number = 1.0 - number
            uv_floats.append(number)
        uv_float_idx += 1
    print('Reads: ', in_obj_filename)
    mesh = openmesh.read_trimesh(in_obj_filename, vertex_normal = True)
    for fh in mesh.faces():
        # print(fh.idx())
        pass

    with open(in_bin_filename, 'rb') as f:
        word = f.read(4)
        while word:
            result = struct.unpack('f', word)[0]
            add_uv_float(result, stride)
            # print(result)
            word = f.read(4)

    print('n_faces: ', mesh.n_faces())
    print('n_vertices: ', mesh.n_vertices())
    print('uv_floats: ', int(len(uv_floats) / 2))

    for i in range(mesh.n_vertices()):
        vh0 = mesh.vertex_handle(i)
        mesh.set_texcoord2D(vh0, (uv_floats[i*2], uv_floats[i*2+1]))

    openmesh.write_mesh(out_filename, mesh, vertex_normal = True, vertex_tex_coord=True)
    print('Writes: ', out_filename)

'''
mtllib head-uv.mtl
usemtl STARTUP_MATERIAL_S80U052_FW00_
'''

# process_mesh('d:/dump/VBV/4169.bin', '../ggs/sol-body.obj', 16, False, '../ggs/sol-body-with-uv.obj')
# process_mesh('d:/dump/VBV/4551.bin', '../ggs/sol-head.obj', 16, False, '../ggs/sol-head-uv.obj')

# process_mesh('d:/dump/VBV/8671.bin', '../ggs/chipp/head.obj', 16, False, '../ggs/chipp/head-uv.obj')
# process_mesh('d:/dump/VBV/7995.bin', '../ggs/chipp/body.obj', 24, False, '../ggs/chipp/body-uv.obj')

# process_mesh('d:/dump/VBV/5755.bin', '../ggs/giovanna/head.obj', 24, True, '../ggs/giovanna/head-uv.obj')
# process_mesh('d:/dump/VBV/5755.bin', '../ggs/giovanna/hair.obj', 24, True, '../ggs/giovanna/hair-uv.obj')
process_mesh('d:/dump/VBV/5812.bin', '../ggs/giovanna/body.obj', 24, True, '../ggs/giovanna/body-uv.obj')
process_mesh('d:/dump/VBV/5812.bin', '../ggs/giovanna/cloth.obj', 24, True, '../ggs/giovanna/cloth-uv.obj')
