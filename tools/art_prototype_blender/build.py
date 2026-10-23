"""PROTOTYPE — descartável. Personagem 3D modelado por script no Blender e renderizado em 8 direções.

Uso (Blender como módulo Python, requer Python 3.11):
    uv venv -p 3.11 .venv-bpy && uv pip install -p .venv-bpy/bin/python bpy
    .venv-bpy/bin/python tools/art_prototype_blender/build.py [tamanho]
Saída: tools/art_prototype_blender/out/knight_<dir>.png (fundo transparente, sombra no chão)

Corpo: malha de "esqueleto" (vértices nas juntas) + modificador Skin + Subdivision, que vira
um corpo orgânico. Armadura e arma: primitivas com materiais PBR (metal, couro, tecido).
Câmera ortográfica a 35° (top-down 3/4); o personagem gira 45° por direção, a luz fica fixa.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path(__file__).parent / "out"
SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 128
DIRS = ["s", "sw", "w", "nw", "n", "ne", "e", "se"]


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color, metallic=0.0, roughness=0.6, noise=0.0, rust=None):
    """Principled BSDF; `noise` varia a rugosidade/cor, `rust` mistura manchas de ferrugem."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if noise or rust:
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 18
        tex.inputs["Detail"].default_value = 8
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.45
        ramp.color_ramp.elements[1].position = 0.75
        links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        if rust:
            mix = nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.inputs["A"].default_value = (*color, 1)
            mix.inputs["B"].default_value = (*rust, 1)
            links.new(ramp.outputs["Color"], mix.inputs["Factor"])
            links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
            inv = nodes.new("ShaderNodeMath")
            inv.operation = "MULTIPLY_ADD"
            inv.inputs[1].default_value = 0.5
            inv.inputs[2].default_value = roughness
            links.new(ramp.outputs["Color"], inv.inputs[0])
            links.new(inv.outputs[0], bsdf.inputs["Roughness"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = noise or 0.15
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def add(obj, mat, parent, smooth=True):
    obj.data.materials.append(mat)
    obj.parent = parent
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def sphere(loc, scale, mat, parent, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    return add(o, mat, parent)


def box(loc, scale, mat, parent, rot=(0, 0, 0), bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    if bevel:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width, m.segments = bevel, 2
    return add(o, mat, parent, smooth=False)


def cylinder(loc, radius, depth, mat, parent, rot=(0, 0, 0), r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=radius, radius2=r2 if r2 is not None else radius,
                                    depth=depth, location=loc, rotation=rot)
    return add(bpy.context.object, mat, parent)


def body(mat, parent):
    """Corpo por modificador Skin: juntas (x, y, z, raio). O personagem olha para -Y."""
    joints = {
        "pelvis": (0, 0, 0.98, 0.15), "spine": (0, 0.01, 1.18, 0.14), "chest": (0, 0, 1.38, 0.17),
        "neck": (0, 0, 1.56, 0.06),
        "l_sh": (0.21, 0, 1.45, 0.075), "l_el": (0.27, 0.02, 1.17, 0.055), "l_wr": (0.29, -0.04, 0.95, 0.042),
        "l_hd": (0.29, -0.06, 0.87, 0.05),
        "r_sh": (-0.21, 0, 1.45, 0.075), "r_el": (-0.27, 0.02, 1.17, 0.055), "r_wr": (-0.29, -0.04, 0.95, 0.042),
        "r_hd": (-0.29, -0.06, 0.87, 0.05),
        "l_hip": (0.1, 0, 0.92, 0.09), "l_kn": (0.115, -0.02, 0.52, 0.065), "l_an": (0.12, 0.01, 0.1, 0.05),
        "l_toe": (0.12, -0.13, 0.04, 0.045),
        "r_hip": (-0.1, 0, 0.92, 0.09), "r_kn": (-0.115, -0.02, 0.52, 0.065), "r_an": (-0.12, 0.01, 0.1, 0.05),
        "r_toe": (-0.12, -0.13, 0.04, 0.045),
    }
    bones = [("pelvis", "spine"), ("spine", "chest"), ("chest", "neck"),
             ("chest", "l_sh"), ("l_sh", "l_el"), ("l_el", "l_wr"), ("l_wr", "l_hd"),
             ("chest", "r_sh"), ("r_sh", "r_el"), ("r_el", "r_wr"), ("r_wr", "r_hd"),
             ("pelvis", "l_hip"), ("l_hip", "l_kn"), ("l_kn", "l_an"), ("l_an", "l_toe"),
             ("pelvis", "r_hip"), ("r_hip", "r_kn"), ("r_kn", "r_an"), ("r_an", "r_toe")]
    names = list(joints)
    mesh = bpy.data.meshes.new("body")
    mesh.from_pydata([joints[n][:3] for n in names], [(names.index(a), names.index(b)) for a, b in bones], [])
    obj = bpy.data.objects.new("body", mesh)
    bpy.context.collection.objects.link(obj)
    obj.modifiers.new("skin", "SKIN")
    for i, n in enumerate(names):
        r = joints[n][3]
        mesh.skin_vertices[0].data[i].radius = (r, r)
    mesh.skin_vertices[0].data[0].use_root = True
    sub = obj.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    obj.data.materials.append(mat)
    obj.parent = parent
    return joints


def knight(root):
    iron = material("iron", (0.11, 0.115, 0.125), metallic=1, roughness=0.38, noise=0.08, rust=(0.22, 0.09, 0.04))
    iron_trim = material("iron_trim", (0.2, 0.2, 0.21), metallic=1, roughness=0.3)
    mail = material("mail", (0.14, 0.14, 0.15), metallic=1, roughness=0.5, noise=0.6)
    cloth = material("cloth", (0.03, 0.028, 0.035), roughness=0.9, noise=0.2)
    tabard = material("tabard", (0.18, 0.025, 0.03), roughness=0.85, noise=0.25)
    leather = material("leather", (0.09, 0.05, 0.03), roughness=0.55, noise=0.3)
    brass = material("brass", (0.45, 0.32, 0.12), metallic=1, roughness=0.35)
    void = material("void", (0, 0, 0), roughness=1)

    j = body(mail, root)
    p = lambda n: Vector(j[n][:3])
    # peitoral, faldas, cinto
    sphere(p("chest") + Vector((0, -0.02, -0.02)), (0.215, 0.165, 0.24), iron, root)
    for k, z in enumerate((1.08, 1.02, 0.96)):
        cylinder((0, 0, z), 0.175 + k * 0.012, 0.07, iron, root, r2=0.185 + k * 0.012)
    cylinder((0, 0, 1.13), 0.18, 0.045, leather, root)
    box((0, -0.18, 1.13), (0.035, 0.012, 0.03), brass, root)
    # tabardo rasgado e capa
    box((0, -0.19, 0.78), (0.11, 0.008, 0.22), tabard, root, rot=(math.radians(-6), 0, 0), bevel=0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.2, 0.86))
    cape = bpy.context.object
    cape.scale = (0.52, 1, 1.4)
    cape.rotation_euler = (math.radians(84), 0, 0)
    sd = cape.modifiers.new("sub", "SUBSURF")
    sd.levels = sd.render_levels = 2
    bend = cape.modifiers.new("bend", "SIMPLE_DEFORM")
    bend.deform_method, bend.angle, bend.deform_axis = "BEND", math.radians(70), "Z"
    sol = cape.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = 0.015
    add(cape, cloth, root)
    for side in (1, -1):
        sh, el, wr, hd = (p(f"{'l' if side > 0 else 'r'}_{n}") for n in ("sh", "el", "wr", "hd"))
        kn, an, toe = (p(f"{'l' if side > 0 else 'r'}_{n}") for n in ("kn", "an", "toe"))
        # ombreiras em camadas com espigão
        sphere(sh + Vector((side * 0.03, 0, 0.03)), (0.13, 0.13, 0.1), iron, root, rot=(0, side * 0.35, 0))
        sphere(sh + Vector((side * 0.06, 0, -0.04)), (0.12, 0.12, 0.07), iron_trim, root, rot=(0, side * 0.6, 0))
        cylinder(sh + Vector((side * 0.09, 0, 0.13)), 0.025, 0.1, iron_trim, root, rot=(0, side * -0.5, 0), r2=0)
        # braçais, cotoveleiras, manoplas
        for a, b, r in ((sh, el, 0.062), (el, wr, 0.052)):
            mid, d = (a + b) / 2, b - a
            cyl = cylinder(mid, r, d.length * 0.85, iron, root)
            cyl.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        sphere(el, (0.07, 0.07, 0.06), iron_trim, root)
        sphere(hd, (0.06, 0.07, 0.07), iron, root)
        # coxotes, joelheiras, grevas, sapatos de placa
        hip = p(f"{'l' if side > 0 else 'r'}_hip")
        for a, b, r in ((hip, kn, 0.085), (kn, an, 0.07)):
            mid, d = (a + b) / 2, b - a
            cyl = cylinder(mid, r, d.length * 0.8, iron, root, r2=r * 0.85)
            cyl.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        sphere(kn + Vector((0, -0.03, 0)), (0.075, 0.07, 0.07), iron_trim, root)
        sphere((an + toe) / 2 + Vector((0, 0, 0.01)), (0.07, 0.13, 0.055), iron, root)
    # elmo fechado com fenda e respiros
    head = Vector((0, 0, 1.71))
    sphere(head, (0.125, 0.135, 0.15), iron, root)
    cylinder(head + Vector((0, 0, -0.07)), 0.118, 0.12, iron, root, r2=0.124)
    box(head + Vector((0, 0, 0.02)), (0.006, 0.14, 0.15), iron_trim, root, bevel=0)
    box(head + Vector((0, -0.125, 0.0)), (0.09, 0.02, 0.012), void, root, bevel=0)
    for dx in (0.04, 0.065):
        for dz in (-0.06, -0.09):
            sphere(head + Vector((-dx, -0.118, dz)), (0.008, 0.01, 0.008), void, root)
    cylinder((0, 0, 1.58), 0.09, 0.08, iron_trim, root, r2=0.07)  # gorjal
    # espada longa na mão esquerda do personagem (+X), lâmina para cima
    hand = p("l_hd")
    steel = material("steel", (0.55, 0.56, 0.58), metallic=1, roughness=0.22, noise=0.05, rust=(0.25, 0.1, 0.05))
    box(hand + Vector((0, -0.02, 0.5)), (0.03, 0.006, 0.42), steel, root, bevel=0.004)
    box(hand + Vector((0, -0.02, 0.07)), (0.11, 0.018, 0.018), iron_trim, root)
    cylinder(hand + Vector((0, -0.02, -0.01)), 0.018, 0.16, leather, root)
    sphere(hand + Vector((0, -0.02, -0.11)), (0.03, 0.03, 0.03), brass, root)


def scene_setup():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = SIZE
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.013, 0.02, 1)
    scene.world = world
    # câmera ortográfica top-down 3/4
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type, cam.data.ortho_scale = "ORTHO", 2.35
    elev = math.radians(35)
    cam.location = (0, -10 * math.cos(elev), 0.95 + 10 * math.sin(elev))
    cam.rotation_euler = (math.radians(90) - elev, 0, 0)
    scene.collection.objects.link(cam)
    scene.camera = cam
    # luz: tocha quente (frente/esquerda), contraluz fria (trás/direita)
    for name, loc, energy, color, size in (("key", (2.2, -2.2, 3.2), 260, (1.0, 0.62, 0.32), 1.2),
                                           ("rim", (-2.0, 2.4, 2.6), 300, (0.45, 0.62, 1.0), 0.6),
                                           ("fill", (-2.5, -2.5, 1.2), 25, (0.5, 0.55, 0.8), 3.0)):
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
        light.data.energy, light.data.color, light.data.size = energy, color, size
        light.location = loc
        light.rotation_euler = (Vector((0, 0, 1.0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(light)
    # chão que só recebe sombra
    bpy.ops.mesh.primitive_plane_add(size=6)
    bpy.context.object.is_shadow_catcher = True


def main():
    OUT.mkdir(exist_ok=True)
    reset()
    scene_setup()
    root = bpy.data.objects.new("knight", None)
    bpy.context.collection.objects.link(root)
    knight(root)
    for i, d in enumerate(DIRS):
        root.rotation_euler = (0, 0, math.radians(45 * i))
        bpy.context.scene.render.filepath = str(OUT / f"knight_{d}_{SIZE}.png")
        bpy.ops.render.render(write_still=True)
    print("ok")


if __name__ == "__main__":
    main()
