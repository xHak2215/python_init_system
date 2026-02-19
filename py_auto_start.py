import os, json, time, sys
import subprocess
import threading
import traceback
import signal
import tpg_mini


path = os.path.abspath(__file__).rsplit("/",1)[0]

with open(os.path.join(path, "config.json"), 'r') as f:
    config = json.load(f)

if not os.path.isdir(os.path.join(path, 'std')):
    os.mkdir(os.path.join(path, 'std'))

processs=[]
log_files=[]
deamons=[]

def strat_p(r_process):
    try:
        name = f"{r_process['dir'].rsplit("/",1)[1]}"
        if os.path.isfile(name):
            name = f"{name}_{round(time.monotonic())}"

        name = os.path.join(path, 'std', name+".log")

        out = open(name, "a")
        devnull = open(os.devnull, 'rb')
        log_files.append(name)

        os.chdir(r_process['dir'])
        processs.append(subprocess.Popen([os.path.join(r_process['venv_dir'], "bin", "python3"), r_process['run_file']],
                        stdout=out, stderr=out, stdin=devnull, start_new_session=True, bufsize=10))
    finally:
        if out: out.close()
        if devnull: devnull.close()

print(f"start ... (pid> {os.getpid()})")
for r_process in config['path']:
    deamons.append(threading.Thread(target=strat_p, args=(r_process,), daemon=True, name=r_process))

status_buff=''

num=0
for s_p in range(len(deamons)):
    deamons[s_p].start()

    while len(processs) == s_p: pass
    data = json.loads(deamons[s_p].name.replace("'", '"'))
    status_buff+=f"[{num}] dir> {data["dir"]} file> {data["run_file"]}  PID> {processs[s_p].pid}\n"
    num+=1


def main_monitor():
        list_p=''
        try:
            while True:
                time.sleep(1.5)
                for s_p in range(len(deamons)):
                    list_p+=f"[{s_p}] status:{"yes" if processs[s_p].poll() is None else processs[s_p].poll()} PID> {processs[s_p].pid}\n"
                
                for file in log_files:
                    if os.path.isfile(file) and os.path.getsize(file) > 80_000:
                        with open(file, 'r+', errors="ignore") as f:
                            content = f.read()
                            f.truncate(0)
                            f.seek(0)
                            f.write(content[80_000:])

                    if os.path.isfile(file) and os.path.getsize(file) > 8_000_000_000:
                        os.remove(file)
                os.system("clear")
                print(f"{status_buff} \n\nprocess: \n{list_p}", end='')

                list_p=''

        except KeyboardInterrupt as e:
            print(e)
            for p in processs:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM) 

        except:
            traceback.print_exc()

def command_interpritation():
    y = tpg_mini.terminal_size()[1]
    if len(processs)>=y:
        y += abs(len(processs)-y)

    while True:
        tpg_mini.move_cursor(0, y)
        command = input(">")

        if command.startswith("rest"):
            index = command.split("rest")[1]
            deamons[index] = threading.Thread(target=strat_p, args=(config['path'][index],), daemon=True, name=config['path'][index])

main_monitor()

