# ! /usr/bin/python
import sys
import socket
import urllib
import gzip
import os

try:
    import pygeoip
except ImportError:
    print("[!} failed to import pygeoip")
    try:
        choice = input("[*] Attempt to install pygeoip? [y/N]")
    except KeyboardInterrupt:
        print("\n user interrupted choice")
    if choice.strip().lower()[0] == "y":
        print("attempting to install pygeoip")
        sys.stdout.flush()
        try:
            import pip

            pip.main(["install", "-q", "pygeoip"])
            import pygeoip

            print("Done")
        except Exception:
            print("Fail")
            sys.exit(1)
    elif choice.strip().lower()[0] == "n":
        print("user denied auto_install")
        sys.exit(1)
    else:
        print("invalid decision")
        sys.exit(1)


class Locator(object):
    def __init__(self, url=False, ip=False, datfile=False):
        self.url = url
        self.ip = ip
        self.datfile = datfile
        self.target = ''

    def check_database(self):
        if not self.datfile:
            self.datfile = "/usr/share/GeoIP/GeoIP.dat"
        else:
            if not os.path.isfile(self.datfile):
                print("failed to detect specified database")
                sys.exit(1)
            return
        if not os.path.isfile(self.datfile):
            print("default database detection failed")
            try:
                choice = input("attempt to auto_install database? [y/N] ")
            except KeyboardInterrupt:
                print("\n user interrupted choice")
                sys.exit(1)
            if choice.strip().lower()[0] == "y":
                print("attempting to install database")
                sys.stdout.flush()
                if not os.path.isdir('/usr/share/GeoIP'):
                    os.makedirs('usr/share/GeoIP')
                    try:
                        urllib.urlretrieve("https://www.miyuru.lk/geoiplegacy",
                                           "/usr/share/GeoIP/GeoIP.dat.gz")
                    except Exception:
                        print("fail")
                        print("failed to download database")
                        sys.exit(1)
                    try:
                        with gzip.open("/usr/share/GeoIP/GeoIP.dat.gz", "rb") as compressed_dat:
                            with open("/usr/share/GeoIP/GeoLiteCity.dat", "wb") as new_dat:
                                new_dat.write(compressed_dat.read())
                    except IOError:
                        print("fail")
                        print("failed to decompress the file")
                        sys.exit(1)
                        os.remove("/usr/share/GeoIP/GeoIP.dat.gz")
                        print("download failed\n")
            elif choice.strip().lower()[0] == "n":
                print("user denied auto install")
            else:
                print("invalid choice")
                sys.exit(1)

    def query(self):
        if not not self.url:
            print(f"translating {self.url}")
            sys.stdout.flush()
            try:
                self.target += socket.gethostbyname(self.url)
                print(self.target)
            except Exception:
                print("\n failed to resolve url")
        else:
            self.target += self.ip
        try:
            print(f"querying for records of {self.target}")
            query_obj = pygeoip.GeoIP(self.datfile)
            for key, value in query_obj.record_by_addr(self.target).items():
                print(f"{key, value}")
                print("\n query complete")
        except Exception:
            print("\n failed to retrieve records")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IP Geolocation Tool")
    parser.add_argument("--url", help="locate an ip based on url", action="store", default=False, dest="url")
    parser.add_argument("-t", "--target", help="locate the specifies ip", default=False, action="store", dest="ip")
    parser.add_argument("--dat", help="custom database filepath", default=False, action="store", dest="datfile")
    args = parser.parse_args()

if ((not not args.url) and (not not args.ip)) or ((not args.url) and (not args.ip)):
    parser.error("invalid target specification")
try:
    locator_object = Locator(url=args.url, ip=args.ip, datfile=args.datfile)
    locator_object.check_database()
    locator_object.query()
except Exception:
    print("\n an unknown error")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n unexpected user input")
    sys.exit(1)
