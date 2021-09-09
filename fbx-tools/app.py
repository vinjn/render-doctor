from FBX_Scene import *
from fbx import *
import math

def DisplayPolygons(pMesh):
    lPolygonCount = pMesh.GetPolygonCount()
    lControlPointCount = pMesh.GetControlPointsCount()
    lControlPoints = pMesh.GetControlPoints()

    print("Polygons:", lPolygonCount)

    vertexId = 0
    total_smooth_normals = [FbxVector4()] * lControlPointCount
    for i in range(lPolygonCount):
        # print("        Polygon ", i)
        lPolygonSize = pMesh.GetPolygonSize(i)
        assert lPolygonSize == 3
        # for l in range(pMesh.GetLayerCount()):
        assert pMesh.GetLayerCount() == 1
        l = 0

        P1 = lControlPoints[pMesh.GetPolygonVertex(i, 0)]
        P2 = lControlPoints[pMesh.GetPolygonVertex(i, 1)]
        P3 = lControlPoints[pMesh.GetPolygonVertex(i, 2)]
        D1: FbxVector4
        D2: FbxVector4
        for idx in range(3):
            if idx == 0:
                D1 = P1 - P3
                D2 = P2 - P1
            elif idx == 1:
                D1 = P2 - P1
                D2 = P3 - P2
            else:
                D1 = P3 - P2
                D2 = P1 - P3

            D1.Normalize()
            D2.Normalize()
            SmoothNormal: FbxVector4 = (P1 - P3).CrossProduct(P2 - P1)
            SmoothNormal.Normalize()
            Angle = math.acos(D1.DotProduct(-D2))
            i1 = pMesh.GetPolygonVertex(i, idx)
            # total_smooth_normals[i1] = total_smooth_normals[i1] + SmoothNormal * Angle

        if False:
            for j in range(lPolygonSize):
                lControlPointIndex = pMesh.GetPolygonVertex(i, j)
                print("            Coordinates: ", lControlPoints[lControlPointIndex])

                leVtxc = pMesh.GetLayer(l).GetVertexColors()
                if leVtxc:
                    header = "            Color vertex (on layer %d): " % l

                    if leVtxc.GetMappingMode() == FbxLayerElement.eByControlPoint:
                        if leVtxc.GetReferenceMode() == FbxLayerElement.eDirect:
                            print(header, leVtxc.GetDirectArray().GetAt(lControlPointIndex))
                        elif leVtxc.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                                id = leVtxc.GetIndexArray().GetAt(lControlPointIndex)
                                print(header, leVtxc.GetDirectArray().GetAt(id))
                    elif leVtxc.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
                            if leVtxc.GetReferenceMode() == FbxLayerElement.eDirect:
                                print(header, leVtxc.GetDirectArray().GetAt(vertexId))
                            elif leVtxc.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
                                id = leVtxc.GetIndexArray().GetAt(vertexId)
                                print(header, leVtxc.GetDirectArray().GetAt(id))
                    elif leVtxc.GetMappingMode() == FbxLayerElement.eByPolygon or \
                            leVtxc.GetMappingMode() ==  FbxLayerElement.eAllSame or \
                            leVtxc.GetMappingMode() ==  FbxLayerElement.eNone:       
                            # doesn't make much sense for UVs
                        pass

                vertexId += 1
            # # end for polygonSize
    # # end for polygonCount

    leNormal = pMesh.GetLayer(l).GetNormals()
    assert leNormal
    assert leNormal.GetMappingMode() == FbxLayerElement.eByControlPoint
    assert leNormal.GetReferenceMode() == FbxLayerElement.eDirect

    for i in range(lControlPointCount):
        total_smooth_normals[i].Normalize()
        leNormal.GetDirectArray().SetAt(i, total_smooth_normals[i])
        # leNormal.GetDirectArray().SetAt(i, FbxVector4(1,0,0,0))
        # print(leNormal.GetDirectArray().GetAt(i))

fbx_file = FBX_Class(r'SKM_Chr_Ply_G_Ciruru_002_A_Body.FBX')
for node in fbx_file.get_scene_nodes():
    if node.GetNodeAttribute() == None: continue
    print(node.GetName(), node.GetNodeAttribute())
    lAttributeType = node.GetNodeAttribute().GetAttributeType()
    if lAttributeType == FbxNodeAttribute.eMesh:
        lMesh = node.GetNodeAttribute ()
        DisplayPolygons(lMesh)
# node = fbx_file.get_node_by_name('head')
# node_property = fbx_file.get_property(node, 'no_export')
# node_property_value = fbx_file.get_property_value( node, 'no_export')
# remove_property = fbx_file.remove_node_property(node, 'no_anim_export')
# remove_property = fbx_file.remove_node_property(node, 'no_export')
# remove_node = fbx_file.remove_nodes_by_names('hair_a_01')
save_file = fbx_file.save(filename=r'untitled.fbx')

