import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import networkx as nx
from scapy.all import *
import matplotlib.pyplot as plt
import numpy as np


# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
#     END = '\033[0m'


class pcap_parser:
    id = 0
    _res = []
    _path = ""

    def __init__(self, path):
        self._res = rdpcap(path).res
        self._path = path

    def __getID__(self):
        self.id += 1
        return self.id

    def __export__(self, key):
        ans = 'z'
        while ans != 'y' and ans != 'n':
            ans = input("\tExport PDF [y/n]? ")
        if ans == 'y':
            try:
                filename = key + str(self.__getID__()) + '.pdf'
                plt.savefig(filename, format='pdf')
                print('\033[92mSucceed! PDF created.\033[0m')
            except SyntaxError:
                print('\033[91mError occurred PDF not created.\033[0m')
        ans = ''
        while ans is not 'y' and ans is not 'n':
            ans = input("\tExport png [y/n]? ")
        if ans is 'y':
            try:
                filename = key + str(self.__getID__()) + '.png'
                plt.savefig(filename, format='png')
                print('\033[92mSucceed! PNG created.\033[0m')
            except ValueError:
                print('\033[91mError occurred PNG not created.\033[0m')
        plt.clf()

    def plot_source_and_destination_count(self):
        src = {}
        dst = {}
        for pkt in self._res:
            if hasattr(pkt.payload, 'src') and hasattr(pkt.payload, 'dst'):
                src.update({pkt.payload.src: 0})
                dst.update({pkt.payload.dst: 0})
        for pkt in self._res:
            if hasattr(pkt.payload, 'src') and hasattr(pkt.payload, 'dst'):
                src[pkt.payload.src] += 1
                dst[pkt.payload.dst] += 1
        sorted_src = []
        sorted_dst = []

        for k in sorted(src):
            sorted_src.append(src[k])
        for k in sorted(dst):
            sorted_dst.append(dst[k])
        plt.bar( sorted_src,range(len(src)), align='center', label='Source', color='blue')
        plt.yticks(range(len(src)), sorted(src.keys()))
        plt.bar(sorted_dst,range(len(dst)),  align='center', label='Destination', color='yellow')
        plt.yticks(range(len(dst)), sorted(dst.keys()))
        plt.title('Sources and Destinations Count')
        plt.legend()
        plt.show()
        plt.bar(range(len(src)), sorted_src, align='center', label='Source', color='green')
        plt.xticks(range(len(src)), sorted(src.keys()))
        plt.bar(range(len(dst)), sorted_dst, align='center', label='Destination', color='red')
        plt.xticks(range(len(dst)), sorted(dst.keys()))
        plt.title('Sources and Destinations Count')
        plt.legend()
        self.__export__('source')

    def plot_protocol_count(self):
        protocol_map = {}
        for pkt in self._res:
            if hasattr(pkt.payload, 'proto'):
                protocol_map.update({pkt.payload.payload.name: 0})
        for pkt in self._res:
            if hasattr(pkt.payload, 'proto'):
                protocol_map[pkt.payload.payload.name] += 1
        sorted_keys = []
        sorted_vals = []

        #colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
        for k in sorted(protocol_map):
            sorted_keys.append(k)
            sorted_vals.append(protocol_map[k])
        # explode = ()
        # for val in range(sorted_vals):
        #     if(val>=1):
        #         explode.insert(0)
        # explode.insert(0.1)

        plt.pie(sorted_vals, labels=sorted_keys, startangle=90, shadow=True, autopct='%1.1f%%')
        plt.title('Protocol Count')
        plt.axis('equal')
        plt.show()
        plt.pie(sorted_vals, labels=sorted_keys, startangle=90, shadow=True, autopct='%1.1f%%')
        plt.title('Protocol Count')
        self.__export__('protocol')

    def plot_ttl_distribution(self):
        bins = range(0, 80, 5)
        # bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
        ttls = []
        for pkt in self._res:
            if hasattr(pkt.payload, 'ttl'):
                ttls.append(pkt.payload.ttl)
        plt.hist(ttls, bins, histtype='bar', rwidth=0.8)
        plt.title('Packet TTL Distribution')
        plt.xlabel('TTL')
        plt.ylabel('Amount')
        plt.show()
        plt.hist(ttls, bins, histtype='bar', rwidth=0.8)
        plt.title('Packet TTL Distribution')
        self.__export__('ttl')

    def plot_source_users_count(self):
        users = {}
        for current in self._res:
            if hasattr(current, 'src'):
                users.update({current.src: 0})
                for pkt in self._res:
                    if hasattr(pkt, 'src') and (current.src == pkt.src):
                        users[current.src] += 1
        total = 0
        for k, v in users.items():
            total += v
        users.update({'Total': total})
        sorted_users = []
        for user in sorted(users):
            sorted_users.append(users[user])
        plt.barh(range(len(users)), sorted_users, color='green')
        plt.yticks(range(len(users)), sorted(users.keys()))
        plt.title('Packets Per Source Count')
        plt.show()
        plt.barh(range(len(users)), sorted_users, color='green')
        plt.yticks(range(len(users)), sorted(users.keys()))
        plt.title('Packets Per Source Count')
        self.__export__('users')

    def clear(self):
        self._res = []

    def plot_connectivity(self):
        G = nx.Graph()
        connections = set()
        nodes = set()
        with PcapReader(self._path) as pcap_reader:
            for p in pcap_reader:
                if hasattr(p.payload, 'src') and hasattr(p.payload, 'dst'):
                    nodes.add(p.src)
                    nodes.add(p.dst)
                    connections.add((p.src, p.dst))
        G.add_nodes_from(nodes)
        G.add_edges_from(connections)
        plt.rcParams['figure.figsize'] = 10, 8
        pos = nx.spring_layout(G, scale=1.0, iterations=100)
        nx.draw(G, pos, node_color='c', edge_color='k', with_labels=True)
        plt.show()
        self.__export__('graph')




def load_file():
    file_num = input('Enter pcap file number or exit to exit(1-6): ')
    if file_num == 'exit': return 0
    print('\tLoading ' + file_num + '.cap file, it may take a few seconds...')
    p = pcap_parser('/home/vitali/PycharmProjects/untitled/' + str(file_num) + '.cap')
    print('\t\033[92mFile loaded!\033[0m')
    return p


def end_plotting():
    end_message1 = '\t\033[94m[any key]\033[0m to continue, \033[92m[n]'
    end_message2 = '\033[0m to load new file \033[91m[exit]\033[0m to exit: '
    file_num = input(end_message1 + end_message2)
    return file_num


def draw_menu():
    print('Main Menu:')
    menu1 = '\t1. Source and destination count. \n\t2. Protocol count. \n\t'
    menu2 = '3. Source user count. \n\t4. TTL Distribution. \n\t5. Network connectivity \n\texit to exit'
    print(menu1 + menu2)
    return input('Enter Option: ')



def input_error():
    print('\t\033[91mWrong entry. Please try again, or [q] to exit\033[0m')


def main():
    while True:
        parser = load_file()
        while True:
            choose = draw_menu()
            if choose is '1':
                parser.plot_source_and_destination_count()
            elif choose is '2':
                parser.plot_protocol_count()
            elif choose is '3':
                parser.plot_source_users_count()
            elif choose is '4':
                parser.plot_ttl_distribution()
            elif choose is '5':
                parser.plot_connectivity()
            elif choose is 'exit':
                return 0
            else:
                input_error()
            file_num = end_plotting()
            print('\n')
            if file_num == 'n':
                parser.clear()
                break
            elif file_num == 'exit':
                return 0


if __name__ == '__main__':
    main()
