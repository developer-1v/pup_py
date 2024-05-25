import os, argparse, subprocess
from print_tricks import pt
pt.easy_imports('pup_py')


from main import main  # Assuming the main functionality is in a function called `main_function`

def main():
    parser = argparse.ArgumentParser(description="Pip Universal Projects CLI")
    parser.add_argument('--run', action='store_true', help='Run the packaging and upload process')
    args = parser.parse_args()

    if args.run:
        main()


# def is_running_in_vscode():
#     # Check for typical VS Code environment variables
#     print(os.environ)
#     return 'VSCODE_CWD' in os.environ or 'VSCODE_IPC_HOOK_CLI' in os.environ

# if __name__ == "__main__":
#     if is_running_in_vscode():
#         print("Running inside VS Code")
#         subprocess.run(['python', '-m', 'pup_py.cli'])
#     else:
#         print("Running from the command line")
#         main()

if __name__ == "__main__":
    main()


