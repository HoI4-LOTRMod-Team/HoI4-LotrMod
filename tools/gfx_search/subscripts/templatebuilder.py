
def write_template(template_path, output_path, replace_dict):
    with open(template_path, 'r') as template:
        t = template.read()
        for key, value in replace_dict.items():
            t = t.replace(key, value)
        
        f = open(output_path, "w")
        f.write(t)
        f.close()
