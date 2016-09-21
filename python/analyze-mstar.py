import glob
import os
import csv
import traceback

writer = csv.DictWriter(open('OD-rMstar-dao.csv', 'wb'),
    ["Grid Name","Grid Rows","Grid Columns","Num Of Agents","Num Of Obstacles","Instance Id",
    'OD-rM* Success', 'OD-rM* Runtime', 'OD-rM* Solution Cost',
    'OD-rM* Generated (HL)', "OD-rM* Look Ahead Nodes Created (HL)",
    "OD-rM* Adoptions (HL)", "OD-rM* Nodes Expanded With Goal Cost (HL)",
    "OD-rM* Conflicts Bypassed With Adoption (HL)", "OD-rM* Expanded (HL)",
    ])
writer.writeheader()
for filename in glob.glob(r'C:\Users\Eli\Documents\Search\Guni\CPF-experiment\bin\Debug\OD-rMstar-dao\*'):
    try:
        #print 'working on', filename
        with open(filename) as f:
            output = f.read()
        output_sans_prefix = output[len(']0;IPython: mstar_public/python'):]
        if output_sans_prefix.strip() == 'Out Of Time' or output_sans_prefix.strip() == 'Error:':
            seconds = 300000.0
            cost = 0
        else:
            lines = output_sans_prefix.splitlines()
            seconds = float(lines[0])
            cost = int(float(lines[1]))
        success = (cost != 0)
        if seconds < 50 and not success:
            print 'failed fast for {}'.format(filename)
        rows = -1
        cols = -1
        obstacles = -1
        basename = os.path.basename(filename)
        grid_name = basename[:len('ost003d')]
        num_agents = int(basename.split('-')[1])
        instance_id = int(basename.split('-')[2].split('_')[0])
        writer.writerow({
            'OD-rM* Success': 1 if success else 0,
            'OD-rM* Solution Cost': cost if success else -2,
            'OD-rM* Runtime': seconds * 1000,
            'Num Of Agents': num_agents,
            'Instance Id': instance_id,
            'Grid Name': grid_name, 
            'Grid Rows': rows,
            'Grid Columns': cols,
            'Num Of Obstacles': obstacles,
            'OD-rM* Generated (HL)':-1, "OD-rM* Look Ahead Nodes Created (HL)":-1,
            "OD-rM* Adoptions (HL)":-1, "OD-rM* Nodes Expanded With Goal Cost (HL)":-1,
            "OD-rM* Conflicts Bypassed With Adoption (HL)":-1, "OD-rM* Expanded (HL)":-1,
        })
    except (ValueError, IndexError), e:
        print 'problem with {}: {}'.format(filename, traceback.format_exc())
        print 'content:', output
        print "delete? (y/n)"
        x = raw_input()
        if x == 'y':
            os.unlink(filename)
        continue
