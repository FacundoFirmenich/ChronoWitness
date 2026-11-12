// Event-driven piecewise-homogeneous CTMC trajectories and bounded-score tests.
// No time grid, tau leaping, empirical resampling pool or fitted noise law.
#include <array>
#include <cassert>
#include <cfloat>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include "assay_config.hpp"
struct Model {int n;double q[2][3][3]{},p[2][3]{};};
double uniform(std::mt19937_64& r){return (double(r()>>11)+.5)*0x1.0p-53;}
int initial(const Model& m,int arm,std::mt19937_64& r){double u=uniform(r),c=0;for(int i=0;i<m.n-1;i++){c+=m.p[arm][i];if(u<c)return i;}return m.n-1;}
struct Observation{double occupation[2]{},raw[2][2]{},endpoint[2][2]{};double max_error=0;};
Observation trajectory(const Model& m,int arm,std::mt19937_64& rng,bool reporters){
    Observation out;int state=initial(m,arm,rng);double occupation=0,report[2]{},integral[2]{};
    for(int pulse=0;pulse<96;pulse++){
        int z=WORDS[arm][pulse%24]-'0';double left=1;
        while(left>0){
            double rate=-m.q[z][state][state];assert(rate>0);
            double wait=-std::log(uniform(rng))/rate,dt=std::min(wait,left),indicator=state==0?1.:0.;
            occupation+=indicator*dt;
            if(reporters)for(int j=0;j<2;j++){
                double gain=-std::expm1(-GAMMAS[j]*dt),old=report[j];
                integral[j]+=indicator*dt+(old-indicator)*gain/GAMMAS[j];
                report[j]=old+(indicator-old)*gain;
            }
            if(wait>=left){left=0;break;}
            left-=wait;double u=uniform(rng)*rate,c=0;int next=-1;
            for(int j=0;j<m.n;j++)if(j!=state){c+=m.q[z][state][j];next=j;if(u<c)break;}
            assert(next>=0&&next!=state);state=next;
        }
        if(pulse==23||pulse==95){int k=pulse==23?0:1;double h=pulse+1;out.occupation[k]=occupation/h;
            assert(out.occupation[k]>=0&&out.occupation[k]<=1+1e-13);
            if(reporters)for(int j=0;j<2;j++){
                out.raw[k][j]=integral[j]/h;out.endpoint[k][j]=report[j];
                out.max_error=std::max(out.max_error,std::abs(out.raw[k][j]+report[j]/(GAMMAS[j]*h)-out.occupation[k]));
            }
        }
    }return out;
}
#if LDBL_MAX_EXP <= 8192
// Some ABIs give long double the same exponent range as double. Keep each
// betting capital as a mantissa times an exact power of two on those targets.
// A term may round away in the current sum while its stored capital survives
// and can recover at a later step.
struct Capital {
    long double mantissa=1;
    int exponent=0;
    void multiply(long double factor) {
        mantissa*=factor;
        if (mantissa!=0 && mantissa<0x1p-512L) {
            mantissa=std::ldexp(mantissa,512);
            exponent-=512;
        }
    }
    long double value() const { return exponent ? std::ldexp(mantissa,exponent) : mantissa; }
};
#else
struct Capital {
    long double capital=1;
    void multiply(long double factor) { capital*=factor; }
    long double value() const { return capital; }
};
#endif
struct Test{
    std::vector<Capital> capital;
    std::vector<long double> stake;double tolerance;int first=0;
    Test(int mixture,double t):tolerance(t){for(double s:STAKES[mixture])stake.push_back(s);capital.resize(2*stake.size());}
    void update(double x,int n){if(first)return;long double sum=0;int k=0;
        for(int sign:{1,-1})for(auto q:stake){long double factor=1+q*(sign*x-tolerance)/(1+tolerance);assert(factor>=-1e-13);auto& term=capital[k++];term.multiply(std::max(0.L,factor));sum+=term.value();}
        if(sum>=20*capital.size())first=n;
    }
};
int main(int argc,char** argv){assert(argc==3);std::ifstream input(argv[1]);int count;input>>count;assert(count==2);std::vector<Model> models(count);
    for(auto& m:models){input>>m.n;assert(m.n==2||m.n==3);for(auto& q:m.q)for(int i=0;i<m.n;i++)for(int j=0;j<m.n;j++)input>>q[i][j];for(auto& p:m.p)for(int i=0;i<m.n;i++)input>>p[i];}assert(input);
    std::string folder=argv[2];std::ofstream validation(folder+"/ASSAY_VALIDATION_RAW.csv"),power(folder+"/ASSAY_POWER_RAW.csv"),benchmark(folder+"/ASSAY_BENCHMARK_RAW.csv");
    validation<<"model,seed,periods,arm,replicates,mean,second_moment,raw_slow,raw_fast,endpoint_slow,endpoint_fast,max_pathwise_error\n"<<std::setprecision(17);
    power<<"model,seed,periods,mixture,tolerance,horizon,replicates,crossings\n"<<std::setprecision(17);
    benchmark<<"probability,tolerance,replicates,crossings\n"<<std::setprecision(17);
    for(int model=0;model<count;model++)for(auto seed:VALIDATION_SEEDS){std::mt19937_64 rng(seed+1009*model);
        for(int arm=0;arm<2;arm++){long double sums[2][6]{};double max_error=0;
            for(int r=0;r<VALIDATION_N;r++){auto v=trajectory(models[model],arm,rng,true);max_error=std::max(max_error,v.max_error);
                for(int k=0;k<2;k++){double x=v.occupation[k];sums[k][0]+=x;sums[k][1]+=x*x;for(int j=0;j<2;j++){sums[k][2+j]+=v.raw[k][j];sums[k][4+j]+=v.endpoint[k][j];}}}
            assert(max_error<2e-12);
            for(int k=0;k<2;k++){validation<<model<<','<<seed<<','<<(k?4:1)<<','<<arm<<','<<VALIDATION_N;for(auto x:sums[k])validation<<','<<double(x/VALIDATION_N);validation<<','<<max_error<<'\n';}
        }std::cerr<<"Validated model "<<model<<" seed "<<seed<<'\n';}
    for(int model=0;model<count;model++)for(auto seed:POWER_SEEDS){std::mt19937_64 rng(seed+1009*model);int hits[2][2][3][3]{};
        for(int r=0;r<POWER_REPLICATES;r++){std::vector<Test> tests;for(int k=0;k<2;k++)for(int mix=0;mix<2;mix++)for(auto t:TOLERANCES)tests.emplace_back(mix,t);
            for(int n=1;n<=HORIZONS[2];n++){auto a=trajectory(models[model],0,rng,false),b=trajectory(models[model],1,rng,false);int ix=0;bool all=true;
                for(int k=0;k<2;k++)for(int mix=0;mix<2;mix++)for(int t=0;t<3;t++){auto& test=tests[ix++];test.update(a.occupation[k]-b.occupation[k],n);all=all&&test.first;}
                if(all)break;
            }
            int ix=0;for(int k=0;k<2;k++)for(int mix=0;mix<2;mix++)for(int t=0;t<3;t++){int crossing=tests[ix++].first;for(int h=0;h<3;h++)if(crossing&&crossing<=HORIZONS[h])hits[k][mix][t][h]++;}
        }
        for(int k=0;k<2;k++)for(int mix=0;mix<2;mix++)for(int t=0;t<3;t++)for(int h=0;h<3;h++)power<<model<<','<<seed<<','<<(k?4:1)<<','<<mix<<','<<TOLERANCES[t]<<','<<HORIZONS[h]<<','<<POWER_REPLICATES<<','<<hits[k][mix][t][h]<<'\n';
        std::cerr<<"Power model "<<model<<" seed "<<seed<<'\n';
    }
    std::mt19937_64 rng(BENCHMARK_SEED);
    for(double p:BENCHMARK_P)for(double t:BENCHMARK_T){int hits=0;for(int r=0;r<BENCHMARK_N;r++){Test test(0,t);for(int n=1;n<=256;n++)test.update(uniform(rng)<p?1.:-1.,n);hits+=test.first>0;}benchmark<<p<<','<<t<<','<<BENCHMARK_N<<','<<hits<<'\n';}
    assert(validation&&power&&benchmark);return 0;
}
