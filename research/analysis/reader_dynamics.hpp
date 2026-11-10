// Reusable exact block dynamics from the baseline phase audit.
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>
using Profile=std::array<long long,8>;
struct Block {int next[4]{};int counts[4][8]{};};
Block block(const std::string& w,int phase,const int* d,int m){
  Block b;
  for(int initial=0;initial<m;++initial){
    int q=initial;
    for(int t=0;t<(int)w.size();++t){int s=w[(phase+t)%w.size()]-'0';++b.counts[initial][2*q+s];q=d[2*q+s];}
    b.next[initial]=q;
  }
  return b;
}
Profile stationary(const Block& b,int initial,int m){
  int seen[4]={-1,-1,-1,-1},path[4],length=0,q=initial;
  while(seen[q]<0){seen[q]=length;path[length++]=q;q=b.next[q];}
  int start=seen[q],period=length-start;
  Profile p{};
  for(int i=start;i<length;++i)for(int j=0;j<2*m;++j)p[j]+=b.counts[path[i]][j]*(12/period);
  return p;
}
bool finite_window_matches(const Block& b,int initial,int m,const Profile& p){
  int q=initial;for(int burn=0;burn<2;++burn)q=b.next[q];
  long long counts[8]{};
  for(int k=0;k<6;++k){for(int j=0;j<2*m;++j)counts[j]+=b.counts[q][j];q=b.next[q];}
  for(int j=0;j<2*m;++j)if(2*counts[j]!=p[j])return false;
  return true;
}
void print_profile(const Profile& p,int m){std::cout<<'[';for(int i=0;i<2*m;++i){if(i)std::cout<<',';std::cout<<p[i];}std::cout<<']';}
void print_delta(const int* d,int m){std::cout<<'[';for(int i=0;i<2*m;++i){if(i)std::cout<<',';std::cout<<d[i];}std::cout<<']';}
