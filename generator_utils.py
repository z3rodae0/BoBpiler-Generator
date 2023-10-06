import yarpgen_utils as y
import csmith_utils as c
import io
import time
import queue
import os

def generator_handshake(p):
    #BOBpiler 프로토콜
    pay = p.stdout.readline() 
    if pay != "[+] generator client hello\n":
        print("[!] generator client hello failed")
        exit(1)
    p.stdin.write("[+] generator server hello\n")
    p.stdin.flush()
    pay = p.stdout.readline()  
    if pay != "[+] done\n":
        print("[!] generator server hello failed")
        exit(1)
    print("[+] generator handshake done!")
    p.stdin.flush()

def generator_clinet(p, generator, code_gen_queue, csmith_path, yarpgen_path):
    #csmith or yarpgen forkserver와 통신하는 client 함수
    while True:
        current_size = code_gen_queue.qsize()
        if code_gen_queue.qsize() < 999:
            if generator == "csmith": 
                print(f"{generator} 넣을게~ 현재 큐의 크기: {current_size}")
                c.csmith_todo(p, code_gen_queue, csmith_path)
            elif generator == "yarpgen": 
                print(f"{generator} 넣을게~ 현재 큐의 크기: {current_size}")
                y.yarpgen_todo(p, code_gen_queue, yarpgen_path)
        else: 
            while code_gen_queue.qsize() >= 1000:
                print("Queue is full. Waiting for space...")
                time.sleep(20)  