import re

def translate_glsl_to_hlsl(glsl_code):
    """
    Translates basic GLSL code to HLSL.
    Handles types, functions, and semantics commonly used in shaders.
    """
    # Translation rules for types
    type_mapping = {
        r'\bvec2\b': 'bool2',
        r'\bvec3\b': 'bool3',
        r'\bvec4\b': 'bool4',
        r'\bivec2\b': 'int2',
        r'\bivec3\b': 'int3',
        r'\bivec4\b': 'int4',
        r'\bvec4\b': 'float4',
        r'\bvec3\b': 'float3',
        r'\bvec2\b': 'float2',
        r'\bmat2\b': 'float2x2',
        r'\bmat3\b': 'float3x3',
        r'\bmat4\b': 'float4x4',
    }

    # Translation rules for functions
    function_mapping = {
        r'\bmix\b': 'lerp',
        r'\bfract\b': 'frac',
        r'\btexture\b': 'Sample',
        r'\bmod\b': 'fmod',
        r'\bdFdx\b': 'ddx',
        r'\bdFdy\b': 'ddy',
    }

    # Translation rules for input/output semantics
    semantic_mapping = {
        r'\blayout\(location = (\d+)\) in\b': lambda m: f'struct INPUT {{ float{m.group(1)} : TEXCOORD{m.group(1)}; }}',
        r'\bout\b': 'out',
        r'\bin\b': 'in',
    }

    # Apply translations
    for pattern, replacement in type_mapping.items():
        glsl_code = re.sub(pattern, replacement, glsl_code)

    for pattern, replacement in function_mapping.items():
        glsl_code = re.sub(pattern, replacement, glsl_code)

    for pattern, replacement in semantic_mapping.items():
        glsl_code = re.sub(pattern, replacement, glsl_code)

    # Fix vector initialization
    glsl_code = re.sub(r'(float[234])\(([^,()]+)\)',
                       lambda m: f'{m.group(1)}({m.group(2)}, {m.group(2)}, {m.group(2)})' if m.group(1) == 'float3' else f'{m.group(1)}({m.group(2)}, {m.group(2)})' if m.group(1) == 'float2' else f'{m.group(1)}({m.group(2)}, {m.group(2)}, {m.group(2)}, {m.group(2)})',
                       glsl_code)

    return glsl_code

def main(input_file, output_file):
    """
    Reads GLSL code from an input file, translates it to HLSL, and writes the result to an output file.
    """
    with open(input_file, 'r') as file:
        glsl_code = file.read()

    hlsl_code = translate_glsl_to_hlsl(glsl_code)

    with open(output_file, 'w') as file:
        file.write(hlsl_code)


main(
    input_file = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\FX\infinite_ocean.glsl',
    output_file = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\FX\infinite_ocean.hlsl'
)
