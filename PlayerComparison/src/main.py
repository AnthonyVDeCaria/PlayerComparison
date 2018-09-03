'''
Created on Jul 31, 2018

@author: Anthony
'''

import pandas as pd
import os
import inspect
from hockey_3D_Map import hockey_3D_Map
import re

csv_headers = ['TOI', 'CA', 'FA', 'SA', 'GA']
toi_threashold = 40 / 60

def check(player_1_name, player_1_data, player_2_name, player_2_data):
    if player_1_data < player_2_data:
        return player_1_name + " less"
    elif player_1_data == player_2_data:
        return "Same"
    else:
        return player_2_name + " less"
        
def extract_player(file_string, player_name):
    file = pd.read_csv(file_string, index_col='Player')
    
    retVal = None
    
    try:
        retVal = file.loc[player_name]
    except KeyError:
        print(player_name + ' is not in ' + file_string)
        
    return retVal 
 
def main(project_folder, data_folder, use_threshold, player_1, player_2):
    if 'NST' in data_folder:
        csv_headers.append('SCA')
        csv_headers.append('HDCA')
       
    init_path = project_folder + '\\out\\' + player_1 + ' - ' + player_2
    games_path = init_path + '\\games'
    analysis_path = init_path + '\\ana'
    
    if not os.path.exists(games_path):
        os.makedirs(games_path)
    if not os.path.exists(analysis_path):
        os.makedirs(analysis_path)
    
    x = hockey_3D_Map(player_1, player_2)
    csvs = []
    player_1_stats = []
    player_2_stats = []
    
    for root, dirs, files in os.walk(project_folder + data_folder):
        for file in files:
            if file.endswith('.csv'):
                print(file)
                
                file_i = os.path.join(root, file)
                player_1_data = extract_player(file_i, player_1)
                player_2_data = extract_player(file_i, player_2)
                
                if(player_1_data is not None) and (player_2_data is not None):
                    csvs.append(file)
                    player_1_stats.append(player_1_data)
                    player_2_stats.append(player_2_data)
                   
    print('\n')
    
    for csv_i, p1_row_i, p2_row_i in zip(csvs, player_1_stats, player_2_stats):
        file_i_name = games_path + '\\' + csv_i.replace('.csv', '.txt')
        game_file_i = open(file_i_name, 'w')
        game_file_i.write(csv_i + '\r\n')
        
        for j in csv_headers:
            p1_stat_j = p1_row_i.loc[j]
            p2_stat_j = p2_row_i.loc[j]
            
            if p1_stat_j == '--':
                p1_stat_j = 0
            else:
                p1_stat_j = float(p1_stat_j)
                
            if p2_stat_j == '--':
                p2_stat_j = 0
            else:
                p2_stat_j = float(p2_stat_j)
            
            string1 = check(player_1, p1_stat_j, player_2, p2_stat_j)
            
            if j == 'TOI':
                if ((p1_stat_j < toi_threashold) or (p2_stat_j < toi_threashold)) and use_threshold:
                    # Go to the next file
                    print(csv_i + ': Failed')
                    game_file_i.close()
                    os.remove(file_i_name)
                    break
                else:
                    x.public_update(string1, csv_i, j)
                    
                    game_file_i.write(j + " -> " + string1 + '\n')
                    game_file_i.write('\t' + '(' + player_1 + ': ' + str(p1_stat_j) + ' vs ' + player_2 + ': ' + str(p2_stat_j) + ')\n')
            else:
                x.public_update(string1, csv_i, j)
                
                game_file_i.write(j + " -> " + string1 + '\n')
                game_file_i.write('\t' + '(' + player_1 + ': ' + str(p1_stat_j) + ' vs ' + player_2 + ': ' + str(p2_stat_j) + ')\n')
                
                p1_toi = p1_row_i.loc['TOI']
                p2_toi = p2_row_i.loc['TOI']
                p1_stat_j_n = float(p1_stat_j) / float(p1_toi)
                p2_stat_j_n = float(p2_stat_j) / float(p2_toi)
                
                string2 = check(player_1, p1_stat_j_n, player_2, p2_stat_j_n)
                game_file_i.write(j + " Normalized -> " + string2 + '\n')
                game_file_i.write('\t' + '(' + player_1 + ': ' + str(p1_stat_j_n) + ' vs ' + player_2 + ': ' + str(p2_stat_j_n) + ')\n')
                
                x.public_update(string2, csv_i, (j+'N'))
        
        game_file_i.close()
    
    key_delimiter = os.path.basename(os.path.normpath(data_folder))
    
    relevant_metrics = ['CAN', 'FAN', 'SAN']
    
    if 'NST' in data_folder:
        analysis_file = open(analysis_path + '\\' + 'NST - ' + key_delimiter + '.txt', 'w')
        relevant_metrics.append('SCAN')
        relevant_metrics.append('HDCAN')
        
        for s in x.situations:
            update_analysis_file(analysis_file, x, s, relevant_metrics, player_1, player_2)
            
    elif 'Corsica' in data_folder:
        analysis_file = open(analysis_path + '\\' + 'Corsica - ' + key_delimiter + '.txt', 'w')
        update_analysis_file(analysis_file, x, 'Total', relevant_metrics, player_1, player_2)
        
    analysis_file.close()

def update_analysis_file(given_file, h_3D, situation, metrics, p1_name, p2_name):
    for m_i in metrics:
        p1_m_i = h_3D.d[p1_name][situation][m_i]
        given_file.write(p1_name + ' total ' + situation + ' for metric ' + m_i + ' -> ' + str(p1_m_i) + '\n')
        
        p2_m_i = h_3D.d[p2_name][situation][m_i]
        given_file.write(p2_name + ' total ' + situation + ' for metric ' + m_i + ' -> ' + str(p2_m_i) + '\n')
        
        same_m_i = h_3D.d['Same'][situation][m_i]
        given_file.write('Same total ' + situation + ' for metric ' + m_i + ' -> ' + str(same_m_i) + '\n')
    given_file.write('\n')
    
def get_toi(given_file_string):
    TOI_LINE_LOCATION = 3
    
    given_file = open(given_file_string, 'r')
    given_file_lines = given_file.readlines()
    toi_line = given_file_lines[TOI_LINE_LOCATION]
    broken_toi_line = toi_line.split(' ')
    
    retVal = []
    
    for value in broken_toi_line:
        value = value.replace(')\n', '')
        try:
            converted_value = float(value)
            retVal.append(converted_value)
        except ValueError:
            pass
            
    return retVal

def get_player(given_file_string, metric):
    given_file = open(given_file_string, 'r')
    check = metric + ' Normalized'
    for line_i in given_file:
        if check in line_i:
            line_i = line_i.replace(check, '').replace(' -> ', '').replace(' less', '')
            return line_i
        
def loop_through_dict(given_dict):
    metrics = ['CA', 'FA', 'SA']
    for m in metrics:
        files_same = 0
        files_different = 0
        for g_c_f, g_n_f in given_dict.items():
            cor_player = get_player(g_c_f, m).strip().lower()
            nst_player = get_player(g_n_f, m).strip().lower()
            
            if(cor_player == nst_player):
                files_same = files_same + 1
            else:
                print(g_c_f)
                files_different = files_different + 1
            
        print(m)
        print('Players the same -> {} \n Players different -> {}'.format(files_same, files_different))
    
def check_toi(project_dir, p1_name, p2_name):
    P1_LOCATION = 0
    P2_LOCATION = 1
    games_folder = project_dir + '\\out\\' + p1_name + ' - ' + p2_name + '\\games'
    
    nst_files = []
    corsica_files = []
    
    problem_files = {}
    good_files = {}
    
    pattern = '- [0-9]{2} [0-9]{2} [0-9]{4} - Total'
    for root, dirs, files in os.walk(games_folder):
        for file in files:
            matchObj = re.search(pattern, file)
            if matchObj:
                if 'Adjusted' in file:
                    corsica_files.append(root + '\\' + file)
                else:
                    nst_files.append(root + '\\' + file)
    
    for nst_i in nst_files:
        pattern1 = '[0-9]{2} [0-9]{2} [0-9]{4}'
        nst_i_timestamp = str(re.search(pattern1, nst_i).group())
        
        for cor_i in corsica_files:
            if re.search(nst_i_timestamp, cor_i):
                break
        
        nst_toi = get_toi(nst_i)
        cor_toi = get_toi(cor_i)
         
        p1_nst_toi = round(nst_toi[P1_LOCATION], 2)
        p2_nst_toi = round(nst_toi[P2_LOCATION], 2)
        p1_cor_toi = round(cor_toi[P1_LOCATION], 2)
        p2_cor_toi = round(cor_toi[P2_LOCATION], 2)
         
        if(p1_nst_toi != p1_cor_toi) or (p2_nst_toi != p2_cor_toi):
            problem_files[cor_i] = nst_i
        else:
            good_files[cor_i] = nst_i
    
    print('Problem Files')
    loop_through_dict(problem_files)
    
    print('Good Files')
    loop_through_dict(good_files)
    
if __name__ == '__main__':
    this_file = os.path.abspath(inspect.getfile(inspect.currentframe()))
    project_dir = os.path.dirname(os.path.dirname(this_file))
    
    player1 = 'James Van Riemsdyk'
    player2 = 'Connor Brown'
    
#     main(project_dir, '\\etc\\Corsica\\by_game\\01 2018', True, player1, player2)

    check_toi(project_dir, player1, player2)
    
    
                    
    
    
    
    