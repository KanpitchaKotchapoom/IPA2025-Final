import subprocess
import os

def showrun(ip, student_id):
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    filename = f"show_run_{student_id}_{ip}.txt"
    command = ['ansible-playbook', 'showrun_playbook.yml', '-i', 'hosts', '-l', ip, '-e', 'f"output_file={filename}"']
    
    if os.path.exists(filename):
        os.remove(filename)

    result = subprocess.run(command, capture_output=True, text=True)
    result_output = result.stdout
    print(result_output)
    print(result.stderr)

    if 'ok=2' in result:
        return 'ok'
    else:
        return 'not okay'