# TODO: raise custom exceptions

#!/usr/bin/env python3
import os, argparse, random, string, json, sys

# import maskpass
from cryptography.fernet import Fernet


class PassGen:

    # def __init__(self):

    def random_password(self, plen, ext):
        base = string.ascii_letters + """1234567890"""
        special = """!@#$%^&*?~`'":;"""
        extend = """+=-_,.|\\}{)(][/><"""
        special_chr = random.choice(special)
        passwd = "".join(random.choices(base, k=plen - 1))
        if ext:
            passwd = "".join(random.choices(base + extend, k=plen - 1))
            return passwd + special_chr
        return passwd + special_chr

        if ext:
            return "".join(random.choices(base + extend, k=plen))
        return "".join(random.choices(base, k=plen))

    def generate_key(self, path):
        if os.path.exists(path):
            raise ValueError(
                f"File already exists {path!r} \033[33mconsider removing --init\033[0m"
            )
        key = Fernet.generate_key()
        with open(path, "wb") as f:
            f.write(key)
        return Fernet(key)

    def load_key(self, path):
        try:
            with open(path, "rb") as f:
                k = f.read()
            return Fernet(k)
        except:
            quit("\n\033[31mCan not read secret.key\033[0m")

    def load_file(self, fpath):
        try:
            with open(fpath, "r") as f:
                return json.load(f)
        except:
            sys.exit(f"\n\033[31mFile {fpath} does not exists or is wrong\033[0m")

    def write_file(self, fpath, data):
        try:
            with open(fpath, "w") as f:
                json.dump(data, f)
        except:
            sys.exit(
                "\n\033[31mSomething goes wrong trying to save to file (Check directory permissions)\033[0m"
            )

    def read_password(self, kpath, fpath, name):
        try:
            fernet = self.load_key(kpath)
            pwdict = self.load_file(fpath)
            if name in pwdict:
                found_pass = fernet.decrypt(bytes(pwdict[name], "utf-8"))
                return str(found_pass, encoding="utf-8")
            return "No result for {name}"
        except:
            sys.exit("\n\033[31mSomething goes wrong, cannot retrieve password.\033[0m")

    def init_only(self, kpath, fpath):
        self.generate_key(kpath)
        self.write_file(fpath, {})

    def write_password(self, kpath, fpath, name, plen, ext):
        try:
            raw_pass = self.random_password(plen, ext)
            if not name:
                return raw_pass
            fernet = self.load_key(kpath)
            pw = str(fernet.encrypt(raw_pass.encode("utf-8")), encoding="utf-8")
            pwdict = self.load_file(fpath)
            if name not in pwdict:
                pwdict[name] = pw
                self.write_file(fpath, pwdict)
                return raw_pass
            else:
                while True:
                    act = input(
                        "Name already exists do you wan't to overwrite it? (Y/N)"
                    )
                    if act == "Y":
                        pwdict[name] = pw
                        self.write_file(fpath, pwdict)
                        return raw_pass
                    elif act == "N":
                        return "Stopped by user request."
        except:
            sys.exit("\n\033[31mSomething goes wrong in password generation\033[0m")

    def find_password(self, name, kpath, fpath):
        fernet = self.load_key(kpath)
        pwdict = self.load_file(fpath)
        if passwd := pwdict.get(name, None):
            return fernet.decrypt(bytes(passwd, "utf-8"))
        return passwd

    def get_all_names(self, fpath):
        pwdict = self.load_file(fpath)
        rows, cols = [], []
        for idx, k in enumerate(pwdict.keys()):
            cols.append(k)
            if (idx + 1) % 4 == 0:
                rows.append("{:>15}{:>15}{:>15}{:>15}".format(*cols))
                cols = []
        rows.append(("{:>15}" * (len(cols))).format(*cols))
        return "\n\033[1;34mList of keys are:\n\033[33m" + "\n".join(rows)


def main(args):
    # create new secret and .enc
    if args.init:
        passgen.init_only(args.k, args.i)
        if args.n is None:
            return "\033[34mKey and encryption files created.\033[0m"
        # # generate and save password after file creatation
        elif args.l < 12:
            raise ValueError("Password length cannot be less than 12 characters")
        raw_pass = passgen.write_password(args.k, args.i, args.n, args.l, args.e)
        return f"\n\033[1mYour password is: \033[32m{raw_pass}\033[0m"
    # List all names
    if args.a:
        return passgen.get_all_names(args.i)
    # Find password for given name
    if args.f:
        raw_pass = passgen.find_password(args.f, args.k, args.i)
        if raw_pass:
            return f"\n\033[1mYour password is: \033[32m{raw_pass}\033[0m"
        return f"\n\033[33mNo saved password for {args.f}\033[0m"
    if args.l < 12:
        raise ValueError("Password length cannot be less than 12 characters")
    # create one time password
    if args.n is None:
        raw_pass = passgen.random_password(args.l, args.e)
        return f"\n\033[1;33mOne time password (no saving): \033[32m{raw_pass}\033[0m"
    # generate and save password
    raw_pass = passgen.write_password(args.k, args.i, args.n, args.l, args.e)
    return f"\n\033[1mYour password is: \033[32m{raw_pass}\033[0m"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random Password Generator")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize and generate encrypted file and key",
    )
    parser.add_argument(
        "-n",
        type=str,
        help="A name for new password, will help you remember and retrieve password easier.",
    )
    parser.add_argument(
        "-f",
        required=False,
        help="Find password for provided name",
    )
    parser.add_argument(
        "-a",
        action="store_true",
        required=False,
        help="List all names used to retrieve passwords",
    )
    parser.add_argument(
        "-k",
        required=False,
        default=os.path.join(os.getcwd(), "secret.key"),
        help="Path to the key (include it's name). default current dir",
    )
    parser.add_argument(
        "-i",
        required=False,
        default=os.path.join(os.getcwd(), "passgen.enc"),
        help="Path to the encrypted file (include it's name). default current dir",
    )
    parser.add_argument(
        "-l",
        required=False,
        type=int,
        default=12,
        help="Length of new random password 8 or higher (default:8)",
    )
    parser.add_argument(
        "-e",
        required=False,
        action="store_true",
        help="If provided password may include +=-_,.|\/{}()[]<> characters.",
    )
    args = parser.parse_args()
    passgen = PassGen()

    try:
        print(main(args))

    except Exception as e:
        print(f"\n\033[31m{e}\033[0m")
