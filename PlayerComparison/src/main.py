'''
Created on Jul 31, 2018

@author: Anthony
'''

import pandas as pd
import os
import inspect

class hockey_3D_Map:
    players = ['Same']
    situations = ['Down 1', 'Leading', 'Tied', 'Total', 'Trailing', 'Up 1', 'Within 1']
    metrics = ['CA', 'CAN', 'FA', 'FAN', 'SA', 'SAN', 'SCA', 'SCAN', 'HDCA', 'HDCAN', 'GA', 'GAN']
    d = {}
    
    def __init__(self, player_1, player_2):
        self.players.append(str(player_1))
        self.players.append(str(player_2))
        
        for p in self.players:
            self.d[p] = {}
            for s in self.situations:
                self.d[p][s] = {}
                for m in self.metrics:
                    self.d[p][s][m] = 0
      
    def public_update(self, check_string, csv_file, metric):
        retVal = False
        
        for p in self.players:
            if p in check_string:
                for s in self.situations:
                    if s in csv_file:
                        retVal = True
                        self.__update(p, s, metric)
                        break
                        
        return retVal
                
    def __update(self, player, situation, metric):
        self.d[player][situation][metric] += 1
                
    def access_total_sum(self, player):
        retVal = 0;
        
        for s in self.situations:
            temp = self.d[player][s]
            for m in self.metrics:
                retVal += temp[m]
                
        return retVal
    
    def access_situation_sum(self, player, situation):
        retVal = 0;
        
        for m in self.metrics:
            retVal += self.d[player][situation][m]
                
        return retVal
    
    def print_d(self, d, indent=0):
        for key, value in d.items():
            if isinstance(value, dict):
                print('\t' * indent + str(key))
                self.print_d(value, indent+1)
            else:
                print('\t' * (indent+1) + str(key) + '\t' + str(value))

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
    csv_headers = ['TOI', 'CA', 'FA', 'SA', 'SCA', 'HDCA', 'GA']
    toi_threashold = 40 / 60
    
    init_path = project_folder + '\\out\\' + player_1 + ' - ' + player_2
    games_path = init_path + '\\games'
    analysis_path = init_path + '\\ana'
    final_path = init_path + '\\fin'
    
    if not os.path.exists(games_path):
        os.makedirs(games_path)
    if not os.path.exists(analysis_path):
        os.makedirs(analysis_path)
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    
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
            string1 = check(player_1, p1_stat_j, player_2, p2_stat_j)
            
            if j == 'TOI':
                if ((p1_stat_j < toi_threashold) or (p2_stat_j < toi_threashold)) and use_threshold:
                    # Go to the next file
                    print(csv_i + ': Failed')
                    game_file_i.close()
                    os.remove(file_i_name)
                    break
                else:
                    game_file_i.write(j + " -> " + string1 + '\n')
            else:
                x.public_update(string1, csv_i, j)
                p1_toi = p1_row_i.loc['TOI']
                p2_toi = p2_row_i.loc['TOI']
                string2 = check(player_1, p1_stat_j/p1_toi, player_2, p2_stat_j/p2_toi)
                game_file_i.write(j + " Normalized -> " + string2 + '\n')
                x.public_update(string2, csv_i, (j+'N'))
        game_file_i.close()
    
    key_delimiter = os.path.basename(os.path.normpath(data_folder))
    
    analysis_file = open(analysis_path + '\\' + key_delimiter + '.txt', 'w')
    analysis_file.write(player_1 + ' complete total ' + str(x.access_total_sum(player_1)) + '\n')
    analysis_file.write(player_2 + ' complete total ' + str(x.access_total_sum(player_2)) + '\n')
    analysis_file.write('Same complete total ' + str(x.access_total_sum('Same')) + '\n')
    analysis_file.write('\n')
    for s in x.situations:
        analysis_file.write(player_1 + ' total ' + s + ' ' + str(x.access_situation_sum(player_1, s)) + '\n')
        analysis_file.write(player_2 + ' total ' + s + ' ' + str(x.access_situation_sum(player_2, s)) + '\n')
        analysis_file.write('Same total ' + s + ' ' + str(x.access_situation_sum('Same', s)) + '\n')
        analysis_file.write('\n')
    analysis_file.close()
    
    final_file = open(final_path + '\\' + key_delimiter + '.txt', 'w')
    relevant_metrics = ['CAN', 'FAN', 'SAN', 'SCAN', 'HDCAN']
    for s in x.situations:
        p1_fn = 0
        p2_fn = 0
        for r_m in relevant_metrics:
            p1_m_i = x.d[player_1][s][r_m]
#             final_file.write(player_1 + ' total ' + s + ' for metric ' + r_m + ' -> ' + str(p1_m_i) + '\n')
            p1_fn += p1_m_i
            
            p2_m_i = x.d[player_2][s][r_m]
#             final_file.write(player_2 + ' total ' + s + ' for metric ' + r_m + ' -> ' + str(p2_m_i) + '\n')
            p2_fn += p2_m_i
        final_file.write(player_1 + ' total ' + s + ' key metrics ' + str(p1_fn) + '\n')
        final_file.write(player_2 + ' total ' + s + ' key metrics ' + str(p2_fn) + '\n')
        final_file.write('\n')
    final_file.close()
    
if __name__ == '__main__':
    this_file = os.path.abspath(inspect.getfile(inspect.currentframe()))
    project_dir = os.path.dirname(os.path.dirname(this_file))
    
    main(project_dir, '\\etc\\by_game\\10 2017', True, 'James van Riemsdyk', 'Connor Brown')
    
    