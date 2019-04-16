import argparse
import shutil
import os
import random


ALL_DMPS = [
'0213',
'0413',
'0423',
'1234',
'1034',
'1024',
]

def get_random_dmp():
    return ALL_DMPS[random.randrange(len(ALL_DMPS))]

def is_sm_ddr_single(chart): return "dance-single" in chart[1]

def split_bars(lines):
    ret = []
    crt = []
    for line in lines:
        line = line.strip()
        if line=='': continue
        if line.startswith(',') or line.startswith(';'):
            ret.append(crt)
            crt = []
        else:
            crt.append(line)
    if len(crt)>=1:
        ret.append(crt)
    return ret

def join_bars(bars):
    ret = []
    for i,bar in enumerate(bars):
        ret+=bar
        if i<len(bars)-1:
            ret+=[',']
        else:
            ret+=[';']
    ret+=['']
    return ret

def dmp_to_pmd(dmp):
    targets = ['x' for _ in range(5)]
    for dkid,char in enumerate(dmp):
        pkid = int(char)
        targets[pkid] = str(dkid)
    return ''.join(targets)

def get_pkid(dmp, dkid):
    return int(dmp[dkid])

def get_dkid(pmd, pkid):
    return None if pmd[pkid]=='x' else int(pmd[pkid])

def apply_dmp_to_line(dmp, ddrline):
    ret = ''
    pmd = dmp_to_pmd(dmp)
    for i in range(5):
        dkid = get_dkid(pmd, i)
        crt = '0' if dkid == None else ddrline[dkid]
        ret += crt
    return ret

def check_conflicts(olddmp, oldaction, newdmp, newaction):
    for i in range(4):
        if oldaction[i]!='0' and newaction[i]!='0':
            if get_pkid(olddmp, i) != get_pkid(newdmp, i):
                return False
    old_only_actions = [i for i in range(4) if oldaction[i]!='0' and newaction[i]=='0']
    new_only_actions = [i for i in range(4) if oldaction[i]=='0' and newaction[i]!='0']
    old_only_pkids = set([get_pkid(olddmp, x) for x in old_only_actions])
    new_only_pkids = set([get_pkid(newdmp, x) for x in new_only_actions])
    if set.intersection(old_only_pkids, new_only_pkids):
        return False
    return True

def rand_matching_dmp(olddmp, oldaction, newaction):
    matched_dmps = [dmp for dmp in ALL_DMPS if check_conflicts(olddmp, oldaction, dmp, newaction)]
    matched_dmps_len = len(matched_dmps)
    if matched_dmps_len==0:
        raise Exception(f'No maching dmp known. olddmp={olddmp}, oldaction={oldaction}, newaction={newaction}')
    return matched_dmps[random.randrange(matched_dmps_len)]

def update_action(oldaction, acting_ddrline):
    ret = ''
    for i in range(4):
        if oldaction[i]=='0' and acting_ddrline[i]=='0':
            newact = '0'
        elif oldaction[i]=='0' and acting_ddrline[i]=='1':
            newact = '1'
        elif oldaction[i]=='0' and acting_ddrline[i]=='2':
            newact = '2'
        elif oldaction[i]=='1' and acting_ddrline[i]=='0':
            newact = '0'
        elif oldaction[i]=='1' and acting_ddrline[i]=='1':
            newact = '1'
        elif oldaction[i]=='1' and acting_ddrline[i]=='2':
            newact = '2'
        elif oldaction[i]=='2' and acting_ddrline[i]=='0':
            newact = '2'
        elif oldaction[i]=='2' and acting_ddrline[i]=='3':
            newact = '1'
        else:
            raise Exception(f"Unexpected actions: oldaction={oldaction}, acting_ddrline={acting_ddrline}")
        ret+=newact
    return ret

def get_incoming_action_in_bar(recent_action, bar):
    for line in bar:
        if line!='0000':
            return update_action(recent_action, line)
    return None

def ddrbar_to_pumpbar(dmp, recent_action, ddrbar):
    ddrbar = [line.replace('M','0') for line in ddrbar]
    incoming_action = get_incoming_action_in_bar(recent_action, ddrbar)
    crtdmp = dmp if incoming_action == None else rand_matching_dmp(dmp,recent_action,incoming_action)
    retbar = []
    for ddrline in ddrbar:
        pumpline = apply_dmp_to_line(crtdmp, ddrline)
        retbar.append(pumpline)
        recent_action = recent_action if ddrline=='0000' else update_action(recent_action, ddrline)
    return crtdmp,recent_action,retbar

def ddrscore_to_pumpscore(ddrscore):
    '''
    @param  ddrscore    DDR score.
    @return             A pump score.
    '''
    dmp = get_random_dmp()
    recent_action = '0000'
    ret = []
    for bar in ddrscore:
        dmp,recent_action,pumpbar = ddrbar_to_pumpbar(dmp, recent_action, bar)
        ret.append(pumpbar)
    return ret

def convert_sm_chart(chart):
    '''
    @param  chart   Lines that makes up a DDR chart in sm format. Includes metadata lines and score lines.
    @returns        PUMP chart lines.
    '''
    # Metadata lines.
    ans = []
    ans.append("#NOTES:")
    ans.append("     pump-single:")
    ans.append("     ddr-piu-convertor:")
    ans.append(chart[3])    # Specifying Easy/Hard/Crazy. For some reason in sm format "Edit" won't work.
    ans.append(chart[4])    # Specifying meter.
    ans.append(chart[5])    # Some weird radar value that I dont understand.

    # Score lines.
    ddr_score = split_bars(chart[6:])
    piu_score = ddrscore_to_pumpscore(ddr_score)
    ans += join_bars(piu_score)
    return ans

def convert_sm(path):
    with open(path, encoding="utf-8") as f: lines = f.readlines()
    lines = [line.replace('\n','').replace('\r','') for line in lines]
    lines = [line for line in lines if not line.strip().startswith('//')]
    chart_starter_indices = [i for i,line in enumerate(lines) if line.strip().startswith(r'#NOTES:')]
    metadata_lines = lines[:chart_starter_indices[0]]
    ans = metadata_lines
    for i,index in enumerate(chart_starter_indices):
        index_end = chart_starter_indices[i+1] if i<len(chart_starter_indices)-1 else len(lines)
        chart = lines[index:index_end]
        print("Chart detected. Showing the first 8 lines.")
        for line in chart[:8]: print(line)
        if is_sm_ddr_single(chart):
            print("Above is a ddr single.")
            ans += convert_sm_chart(chart)
        else:
            print("Above is NOT a ddr single.")
    ans = [line+'\n' for line in ans]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(ans)


def work(random_seed, input_path, output_path):
    '''
    @param random_seed
    @param input_path   Path to a song folder containing DDR charts.
    @param output_path  Path to the new folder that will be created with generated PIU charts.
    '''
    if random_seed != None:
        random.seed(hash(random_seed))
    shutil.copytree(input_path, output_path)
    sscfiles = [filename for filename in os.listdir(output_path) if filename[-4:]=='.ssc']
    smfiles = [filename for filename in os.listdir(output_path) if filename[-3:]=='.sm']
    if len(sscfiles) >= 1:
        convert_ssc(os.path.join(output_path, sscfiles[0]))
    elif len(smfiles) >= 1:
        convert_sm(os.path.join(output_path, smfiles[0]))
    else:
        raise Exception("No ssc or sm file found.")

def main():
    arg_parser = argparse.ArgumentParser(description="Generate PIU single charts from DDR single charts.")
    arg_parser.add_argument("--input", required=True, help="Path to the input song.")
    arg_parser.add_argument("--output", help="Path to the output song.")
    arg_parser.add_argument("--random-seed", help="Random string as the seed.")
    args = arg_parser.parse_args()
    work(args.random_seed, args.input, args.output)

if __name__=='__main__':
    main()
