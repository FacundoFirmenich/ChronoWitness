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
int main(int argc,char**argv){
  if(argc!=3)return 2;
  std::string a=argv[1],b=argv[2];
  if(a.size()!=24||b.size()!=24)return 3;
  for(char c:a+b)if(c!='0'&&c!='1')return 4;
  std::cout<<"{\"scope\":\"Exact mathematical design ensemble;not biological data\",\"profile_scale\":12,\"stationary_profile_denominator\":288,\"phase_mean_from_sum_denominator\":6912,\"classes\":[";
  for(int m=1;m<=4;++m){
    long long total=1;for(int i=0;i<2*m;++i)total*=m;
    long long fixed_cases=0,mean_cases=0,ensemble_cases=0,commonphase_cases=0,finite_checks=0;
    bool first_mean=true,first_ensemble=true;
    std::string mean_witness="null",ensemble_witness="null";
    for(long long code=0;code<total;++code){
      int d[8]{};long long value=code;
      for(int i=2*m-1;i>=0;--i){d[i]=value%m;value/=m;}
      std::array<Profile,4> sum_a{},sum_b{};
      std::array<std::vector<Profile>,4> profiles_a,profiles_b;
      for(int phase=0;phase<24;++phase){
        Block ba=block(a,phase,d,m),bb=block(b,phase,d,m);
        for(int q=0;q<m;++q){
          Profile pa=stationary(ba,q,m),pb=stationary(bb,q,m);
          if(m<=3){
            if(!finite_window_matches(ba,q,m,pa)||!finite_window_matches(bb,q,m,pb))return 5;
            finite_checks+=2;
          }
          if(pa!=pb){++commonphase_cases;if(phase==0)++fixed_cases;}
          for(int j=0;j<2*m;++j){sum_a[q][j]+=pa[j];sum_b[q][j]+=pb[j];}
          profiles_a[q].push_back(pa);profiles_b[q].push_back(pb);
        }
      }
      for(int q=0;q<m;++q){
        if(sum_a[q]!=sum_b[q]){
          ++mean_cases;
          if(first_mean){
            std::cout<<"";
            // Record in a compact independent string, without floating point.
            std::string s="{\"delta\":[";
            for(int i=0;i<2*m;++i){if(i)s+=",";s+=std::to_string(d[i]);}
            s+="],\"q0\":"+std::to_string(q)+",\"sum_scaled_A\":[";
            for(int i=0;i<2*m;++i){if(i)s+=",";s+=std::to_string(sum_a[q][i]);}
            s+="],\"sum_scaled_B\":[";
            for(int i=0;i<2*m;++i){if(i)s+=",";s+=std::to_string(sum_b[q][i]);}
            s+="]}";mean_witness=s;first_mean=false;
          }
        }
        std::sort(profiles_a[q].begin(),profiles_a[q].end());
        std::sort(profiles_b[q].begin(),profiles_b[q].end());
        if(profiles_a[q]!=profiles_b[q]){
          ++ensemble_cases;
          if(first_ensemble){
            std::string s="{\"delta\":[";
            for(int i=0;i<2*m;++i){if(i)s+=",";s+=std::to_string(d[i]);}
            s+="],\"q0\":"+std::to_string(q)+"}";ensemble_witness=s;first_ensemble=false;
          }
        }
      }
    }
    if(m>1)std::cout<<',';
    std::cout<<"{\"states\":"<<m<<",\"transition_functions\":"<<total<<",\"initial_state_cases\":"<<total*m
      <<",\"fixed_phase0_separating_cases\":"<<fixed_cases<<",\"common_phase_separating_cases\":"<<commonphase_cases
      <<",\"phase_mean_separating_cases\":"<<mean_cases<<",\"phase_profile_multiset_separating_cases\":"<<ensemble_cases
      <<",\"finite_window_checks_burn2_measure6\":"<<finite_checks
      <<",\"first_phase_mean_witness\":"<<mean_witness<<",\"first_phase_multiset_witness\":"<<ensemble_witness<<'}';
  }
  std::cout<<"]}\n";
}
