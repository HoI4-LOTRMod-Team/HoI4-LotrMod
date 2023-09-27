import argparse
import subprocess
import os
import sys
import time

# Get the available subscripts in the /subscripts folder
def get_available_subscripts():
    script_files = [file[:-3] for file in os.listdir("subscripts") if file.endswith(".py")]
    return script_files

# Run the given subscript
def run_subscript(subscript_name, output_file, args):
    loading_chars = ["|", "/", "-", "\\"]
    
    print("Running the subscript...")
    
    script_dir = os.path.dirname(os.path.abspath(f"subscripts/{subscript_name}.py"))
    
    # Temporarily change the working directory to the subscript's directory
    original_cwd = os.getcwd()
    os.chdir(script_dir)
    
    subprocess.run(["python", f"{subscript_name}.py", *args], stdout=output_file, text=True)
    
    # Change back to the original working directory
    os.chdir(original_cwd)

# main program
def main():
    parser = argparse.ArgumentParser(description="LOTR Mod GFX-Maker script.")
    parser.add_argument("-s", "--subscript", nargs="?", help="Name of the subscript to run (without .py extension)")
    parser.add_argument("-o", "--outputfile", nargs="?", help="Output file to save the output of the subscript")
    parser.add_argument("args", nargs="*", help="Additional arguments to pass to the subscript")
    
    args = parser.parse_args()
    
    available_subscripts = get_available_subscripts()
    
    used_args = True
    if args.subscript is None:
        used_args = False
        print("Welcome to the LOTR Mod GFX-Maker script!")
        print("Available subscripts:", ", ".join(available_subscripts))
        args.subscript = input("Please enter the subscript you want to run: ")
        
    if args.subscript not in available_subscripts:
        used_args = False
        print(f"Error: '{args.subscript}' is not a valid subscript.")
        return
    
    if args.outputfile is None:
        args.outputfile = input("Enter the name of the output .gfx file you want to write to (inside of /interface): ")
    
    # Ensure that the output file ends with ".gfx"
    if not args.outputfile.endswith(".gfx"):
        args.outputfile += ".gfx"
    output_path = f"../interface/auto_generated/{args.outputfile}"
    
    with open(output_path, "w") as output_file:
        run_subscript(args.subscript, output_file, args.args)
    
    print(f"Output written to {output_path}")
    
    if(used_args is False):
        print("\nNote: You can provide arguments directly like this: \npython make_gfx.py -s [subscript] -o [outputfile] [other args]")

if __name__ == "__main__":
    main()
