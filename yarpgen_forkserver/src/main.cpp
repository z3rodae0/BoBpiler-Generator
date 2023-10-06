/*
Copyright (c) 2015-2020, Intel Corporation
Copyright (c) 2019-2020, University of Utah

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

//////////////////////////////////////////////////////////////////////////////
#include "options.h"
#include "program.h"
#include "utils.h"
#include <iostream>
#include <string>
#include <vector>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <ostream>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>
#include <sstream> 

using namespace yarpgen;

static unsigned long g_seed = 0; // 글로벌 시드 변수
static unsigned long g_mutation_seed = 0; // 글로벌 뮤테이션 시드 변수

void generator_hand_shake() {
    std::cout << "[+] generator client hello\n";
    std::cout.flush();
    char l_server_pay[30] = {0}; // Initialize with zeros
    read(0, l_server_pay, 30);   // Read one byte less to account for the NULL terminator
    l_server_pay[29] = '\0';     // Null-terminate the string
    
    if(strcmp(l_server_pay, "[+] generator server hello\n")) {
        exit(1);
    }
    std::cout << "[+] done\n";
	std::cout.flush();
}

void init_options(int p_argc, char *p_argv[], uint64_t p_seed, uint64_t p_mutation_seed ,std::string p_o_dir){
    OptionParser::initOptions();
    OptionParser::parse(p_argc, p_argv); //사실상 이거 필요도 없음 그냥 여기서 옵션 다 세팅해주는 함수 호출하면 됨,그냥 subprocess로 yargpen만 해도됨
    Options &options = Options::getInstance();

    /*시드 랜덤 값*/
    options.setSeed(p_seed);
    rand_val_gen = std::make_shared<RandValGen>(options.getSeed()); //RandValGen이라는 생성자에다가 인자로 시드를 넘겨줌

    /*뮤테이션 시드 랜덤 값*/
    options.setMutationSeed(g_mutation_seed);
    rand_val_gen -> setMutationSeed(options.getMutationSeed()); //mutation_seed == 0이라면 rd()으로 랜덤 시드

    /*출력 소스 디렉토리*/
    options.setOutDir(p_o_dir); //program.cpp에서 getOutDir를 통해서 디렉토리 세팅함
}

void child_process(){

    ProgramGenerator new_program;
    new_program.emit();
	exit(0);
}

/*string -> unsigned long 및 g_random = p_seed*/
void seed_To_g_seed(std::string p_seed){ 
    /*Local seed를 global g_Seed에 저장해주는 함수*/
    try {
        g_seed = std::stoul(p_seed); // string to unsigned long
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: Invalid argument. The string doesn't represent a valid number." << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: Out of range. The string represents a number that's too large or small for unsigned long." << std::endl;
    }
}

void seed_To_g_mutation_seed(std::string p_mutation_seed){ 
    /*Local seed를 global g_Seed에 저장해주는 함수*/
    try {
        g_mutation_seed = std::stoul(p_mutation_seed); // string to unsigned long
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error: Invalid argument. The string doesn't represent a valid number." << std::endl;
    } catch (const std::out_of_range& e) {
        std::cerr << "Error: Out of range. The string represents a number that's too large or small for unsigned long." << std::endl;
    }
}

int find_or_symbols(const std::string& p_file_seed, std::string& p_o_dir, std::string& p_seed, std::string& p_mutation_seed){
    size_t first_pipe_pos = p_file_seed.find('|');

    if (first_pipe_pos != std::string::npos) {
        p_o_dir = p_file_seed.substr(0, first_pipe_pos); // 첫 번째 '|' 앞의 부분
        size_t second_pipe_pos = p_file_seed.find('|', first_pipe_pos + 1);
        
        if (second_pipe_pos != std::string::npos) {
            p_seed = p_file_seed.substr(first_pipe_pos + 1, second_pipe_pos - first_pipe_pos - 1); // 첫 번째 '|' 다음과 두 번째 '|' 앞의 부분
            p_mutation_seed = p_file_seed.substr(second_pipe_pos + 1); // 두 번째 '|' 다음의 부분
            return 0;
        }
    }

    std::cerr << "Invalid input format. Please enter 'filename|seed|mutation_seed'." << std::endl;
    return 1;
}

int main(int argc, char *argv[]) {
    generator_hand_shake(); //BoB Protocol

    while(1){
        std::string l_dir_seed; // 입력 페이로드
		std::string l_o_dir; // 디렉토리 경로
		std::string l_seed;  //시드
        std::string l_mutation_seed; //뮤테이션 시드

		std::getline(std::cin, l_dir_seed);
        find_or_symbols(l_dir_seed, l_o_dir, l_seed, l_mutation_seed); // | |
		seed_To_g_seed(l_seed); //g__seed = l_seed
        seed_To_g_mutation_seed(l_mutation_seed); //g_mutation_seed = l_mutation_seed

        /*forkserver start*/
        pid_t l_pid = 0;
        l_pid = fork();
        if(l_pid == (-1)){
            perror("[!] fork failed\n");
            std::cout.flush();
            exit(1);
        }
        else if(l_pid == 0){ 
            /*시드, 뮤테이션 시드, 파일이름 옵션 세팅*/
            init_options(argc, argv, g_seed, g_mutation_seed, l_o_dir); 
            child_process();
        }
        else{
            int l_status;
            waitpid(l_pid, &l_status, 0);
            
            std::stringstream json_stream;
            json_stream << "{";
            json_stream << " \"generator\": \"yarpgen\",";
            json_stream << " \"return_code\": \"" << l_status << "\"";
            json_stream << "}";
            std::cout << json_stream.str() << std::endl;
            std::cout.flush();
        }
    }
    return 0;
}