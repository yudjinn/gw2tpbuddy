from gw2api import GW2Client
from enum import Enum
import yaml
import shelve
import os

class GW2:
    races=['Asura','Charr','Norn','Human','Sylvari']
    genders=['Male','Female']
    professions = ['Warrior', 'Ranger', 'Revenant', 'Thief', 'Elementalist', 'Mesmer', 'Engineer', 'Guardian', 'Necromancer']

    def __init__(self,load="cache",filename='shelve2'):
        self.config = self.load_config()
        self.gw2_clients = []

        for account in self.config['accounts']:
            self.gw2_clients.append({'name':account['name'],'client':GW2Client(api_key=account['key'])})
        self.reduced={}
        load=self.config['cache']['load']

        if load =="refresh":
            self._load_refresh(filename)
        elif load == "cache":
            self._load_cache(filename)
        else:
            self._load_merge(filename)

    def load_config(self):
        found=False
        config_file=''
        for try_config in ['config.yml']:
            if os.path.isfile(try_config):
                found=True
                config_file=try_config
                break
        if found:
            with open(config_file, 'r') as conf:
                return yaml.load(conf, yaml.SafeLoader)
        else:
            print('Cannot find config.yml file')
            return {}

    def _load_merge(self, filename):
        with shelve.open(filename) as db:
            for k, v in db.items():
                self.reduced[k]=v
            for account in self.gw2_clients:
                characters = account['client'].characters.get()
                for name in characters:
                    if name not in db:
                        print(f'{name} is new')
                        c=account['client'].characters.get(id=name)
                        self.reduced[name] = {
                            'name':c['name'],
                            'race':c['race'],
                            'gender':c['gender'],
                            'profession':c['profession'],
                            'account':c['account'],
                            'created':c['created']
                        }
                        db[name]=self.reduced[name]

    def _load_refresh(self,filename):
        self.reduced = {}
        for account in self.gw2_clients:
            characters = account['client'].characters.get()
            info = {
            x['name']: x for x in (
            account['client'].characters.get(id=c) for c in characters)
            }
            # import json
            # print(json.dumps(info))
            # exit(1)
            self.reduced.update({x['name']: {
                'name': x['name'],
                'race': x['race'],
                'gender': x['gender'],
                'profession': x['profession'],
                'account': account['name'],
                'created': x['created']
            } for x in info.values()})
            with shelve.open(filename, flag='n') as db:
                for k, v in self.reduced.items():
                  db[k] = v

    def _load_cache(self, filename):
        self.reduced = {}
        with shelve.open(filename) as db:
            for k, v in db.items():
                self.reduced[k] = v

    def find(self, race, gender, profession, all=False):
        ret = []
        for c in self.reduced.values():
            if c['race'] == race and c['gender'] == gender and c['profession'] == profession:
                if all:
                    ret.append(c)
                else:
                    return c
        if all:
            return ret
        return False

    def find_missing(self, profession):
        missing = []
        for race in self.races:
            for gender in self.genders:
                if not self.find(race, gender, profession):
                    missing.append((race, gender, profession))
        return missing

    def represent(self):
        reps = {}
        for race in GW2.races:
            reps[race] = {}
            for gender in GW2.genders:
                reps[race][gender] = []
        for c in self.reduced.values():
            reps[c['race']][c['gender']].append((c['profession'], c['name']))
        return reps

    def birthdays(self):
        from datetime import date, datetime
        def keyfun(c):
            dt=datetime.strptime(c['created'], "%Y-%m-%dT%H:%M:%SZ")
            return (dt.month, dt.day, dt.hour, dt.minute, dt.second)
        list_of_characters=sorted(list(GW2.reduced.values()), key=keyfun)
        today=date.today()
        found=False
        first=False
        for c in list_of_characters:
            if first and found:
                first=False
            if not first and not found and today > datetime.strptime(c['created'], "%Y-%m-%dT%H:%M:%SZ").date().replace(year=today.year):
                first=True
                found=True
            prefix='*' if first else ' '
            print(prefix + str(c))
