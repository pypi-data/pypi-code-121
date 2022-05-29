def save_obj(filename, vertices, faces=None, colors=None):
    """保存obj文件
    vertices: shape Nx3
    faces: shape Mx3
    """

    if colors is not None:
        assert colors.shape == vertices.shape

    with open(filename, "w") as fw:
        if colors is None:
            for i in range(vertices.shape[0]):
                x, y, z = vertices[i]
                r, g, b = 0.5, 0.5, 0.5
                fw.write(f"v {x} {y} {z} {r} {g} {b}\n")
        else:
            for i in range(vertices.shape[0]):
                x, y, z = vertices[i]
                r, g, b = colors[i]
                fw.write(f"v {x} {y} {z} {r} {g} {b}\n")

        if faces is not None:
            for i in range(faces.shape[0]):
                a = faces[i][0]
                b = faces[i][1]
                c = faces[i][2]
                fw.write(f"f {a+1} {b+1} {c+1}\n")
