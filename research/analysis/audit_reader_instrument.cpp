// Complete one-way binary 2-state reader x 2-state instrument ensemble.
// Exact design objects only. No biological or experimental data are generated.
#include "reader_dynamics.hpp"
#include <numeric>
int main(int argc,char**argv){
 if(argc!=3)return 2;
 std::string a=argv[1],b=argv[2];if(a.size()!=24||b.size()!=24)return 3;
 long long tables=0,full_mean_sep=0,full_law_sep=0,det_mean_sep=0,det_law_sep=0;
 bool found=false;int first_d[8]{},first_f[4]{},first_g[8]{},first_q=0;long long first_a=0,first_b=0;
 for(int fc=0;fc<16;++fc)for(int gc=0;gc<256;++gc){
  int f[4]{},g[8]{},d[8]{};for(int i=0;i<4;++i)f[i]=(fc>>(3-i))&1;
  for(int i=0;i<8;++i)g[i]=(gc>>(7-i))&1;
  for(int q=0;q<4;++q)for(int z=0;z<2;++z)d[2*q+z]=2*f[2*(q/2)+z]+g[2*q+z];
  ++tables;
  for(int q0=0;q0<4;++q0){
   Profile ma{},mb{};std::vector<Profile> pa,pb;std::vector<long long> da,db;long long sa=0,sb=0;
   for(int phase=0;phase<24;++phase){
    auto xa=stationary(block(a,phase,d,4),q0,4),xb=stationary(block(b,phase,d,4),q0,4);
    pa.push_back(xa);pb.push_back(xb);long long va=0,vb=0;
    for(int j=0;j<8;++j){ma[j]+=xa[j];mb[j]+=xb[j];if((j/2)%2==1){va+=xa[j];vb+=xb[j];}}
    da.push_back(va);db.push_back(vb);sa+=va;sb+=vb;
   }
   full_mean_sep+=(ma!=mb);std::sort(pa.begin(),pa.end());std::sort(pb.begin(),pb.end());full_law_sep+=(pa!=pb);
   det_mean_sep+=(sa!=sb);std::sort(da.begin(),da.end());std::sort(db.begin(),db.end());det_law_sep+=(da!=db);
   if(sa!=sb&&!found){found=true;for(int i=0;i<8;++i){first_d[i]=d[i];first_g[i]=g[i];}for(int i=0;i<4;++i)first_f[i]=f[i];first_q=q0;first_a=sa;first_b=sb;}
  }
 }
 std::cout<<"{\"scope\":\"Exact FD7 one-way reader-instrument cascade; not biological data\",\"upstream_states\":2,\"instrument_states\":2,\"transition_tables\":"<<tables<<",\"table_initial_pairs\":"<<tables*4<<",\"phase_mean_full_profile_separators\":"<<full_mean_sep<<",\"phase_law_full_profile_separators\":"<<full_law_sep<<",\"phase_mean_instrument_bit_separators\":"<<det_mean_sep<<",\"phase_law_instrument_bit_separators\":"<<det_law_sep<<",\"first_instrument_mean_witness\":";
 if(!found)std::cout<<"null";else{
  std::cout<<"{\"delta\":";print_delta(first_d,4);std::cout<<",\"reader_delta\":";print_delta(first_f,2);std::cout<<",\"instrument_delta_by_joint_state_input\":";print_delta(first_g,4);
  std::cout<<",\"initial_joint_state\":"<<first_q<<",\"mean_scaled_sum_A\":"<<first_a<<",\"mean_scaled_sum_B\":"<<first_b<<",\"normalization_to_time_fraction\":6912}";
 }
 std::cout<<"}\n";
}
