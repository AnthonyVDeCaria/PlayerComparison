'''
Created on Aug 21, 2018

@author: Anthony
'''

class hockey_3D_Map:
    players = ['Same']
    situations = ['Down 1', 'Leading', 'Tied', 'Total', 'Trailing', 'Up 1', 'Within 1']
    metrics = ['TOI', 'CA', 'CAN', 'FA', 'FAN', 'SA', 'SAN', 'SCA', 'SCAN', 'HDCA', 'HDCAN', 'GA', 'GAN']
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
    
    