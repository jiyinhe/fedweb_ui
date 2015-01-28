rm(list=ls())

prepare_data<-function(datafile){
    # laod data from csv    
    data<-read.csv(datafile)
    # tranform user quality to factors
    data$u_level<-factor(data$u_quality)

    # also prepare level data
    qd_levels <- continous_to_level(data$q_difficulty)
    data$qd_high <- qd_levels$d_high
    data$qd_low <- qd_levels$d_low

    fe_levels <- continous_to_level(data$f_entropy)
    data$fe_high <- fe_levels$d_high
    data$fe_low <- fe_levels$d_low

    fr_levels <- continous_to_level(data$f_relevance)
    data$fr_high <- fr_levels$d_high
    data$fr_low <- fr_levels$d_low

    newdata<-list(data=data, 
        qd_levels=qd_levels, fe_levels=fe_levels,fr_levels=fr_levels)
    return(newdata)
}

# input the training data, make new IV values for plot 
make_testdata<-function(data){
    # Generate prediction data for plot
    # create X data points
    # 4 u_levels
    u_levels<-factor(c(0, 0.1, 0.5, 1))
    # f_entropy between [c, d]
    f_entropy<-seq(from=min(data$f_entropy), to=max(data$f_entropy), length.out=100)
    # f_relevance 
    f_relevance<-seq(from=min(data$f_relevance), to=max(data$f_relevance), length.out=100)
    # q_difficulty between [a, b]
    q_difficulty<-seq(from=min(data$q_difficulty),to=max(data$q_difficulty),length.out=100)
    # store them
    newdata<-list(u_level=u_levels, f_entropy=f_entropy, 
            f_relevance=f_relevance, q_difficulty=q_difficulty,
            fe_median=median(data$f_entropy), fr_median=median(data$f_relevance), 
            qd_median=median(data$q_difficulty))
    return(newdata)
}

continous_to_level<-function(data){
    high<-quantile(data, 0.75)
    low<-quantile(data, 0.25)
    recenter_high <- data - high
    recenter_low <- data - low
    levels<-list(high=high, low=low, d_high=recenter_high, d_low=recenter_low)
    return(levels)
}

model_train_predict<-function(model, train_data, test_data, outputfile){
    # first train the model
    mod <-(glm(model, data=train_data, family=binomial(link = logit))) 
    # prepare the test_data
    input<-expand.grid(test_data)
    # make predictions
    tmp<-cbind(input, predict(mod, newdata=input, type="link", se=TRUE))
    newdata<-within(tmp, {
         predictedProb<-plogis(fit)
         LL<-plogis(fit-(1.96*se.fit))
        UL<-plogis(fit+(1.96*se.fit))
    })
    write.table(newdata, outputfile)
}


# Task 1 
# data for test 1
rawdata<-prepare_data('data/smooth_data_task1.csv')
data<-rawdata$data
qd_level<-rawdata$qd_levels
fe_level<-rawdata$fe_levels
fr_level<-rawdata$fr_levels

# prepare test data
testdata<-make_testdata(data)

# ============================================================
# q_difficulty x u_level: fix f_entropy, f_relevance
# model
mod<-diff ~ q_difficulty + u_level + f_entropy + q_difficulty:u_level + q_difficulty:f_entropy
# input for predict
input<-list(q_difficulty=testdata[['q_difficulty']], u_level=testdata[['u_level']],
    f_entropy=testdata[['fe_median']], f_relevance=testdata[['fr_median']])
outputfile <- 'data/lr_1_qxu.txt'
model_train_predict(mod, data, input, outputfile)

# ============================================================
# q_difficulty:f_entropy: fix f_relevance, level q_difficulty
# high
mod<-diff ~ qd_high + u_level + f_entropy + qd_high:u_level + qd_high:f_entropy
# input for predict
input<-list(qd_high=qd_level$high, u_level=testdata[['u_level']],
    f_entropy=testdata[['f_entropy']], f_relevance=testdata[['fr_median']])

outputfile<-'data/lr_1_qxfe_high.txt'
model_train_predict(mod, data, input, outputfile)

# low
mod<-diff ~ qd_low + u_level + f_entropy + qd_low:u_level + qd_low:f_entropy
input<-list(qd_low=qd_level$low, u_level=testdata[['u_level']],
    f_entropy=testdata[['f_entropy']], f_relevance=testdata[['fr_median']])

outputfile<-'data/lr_1_qxfe_low.txt'
model_train_predict(mod, data, input, outputfile)



# ============================================================
# Task 10 
# data for test 10
rawdata<-prepare_data('data/smooth_data_task10.csv')
data<-rawdata$data
qd_level<-rawdata$qd_levels
fe_level<-rawdata$fe_levels
fr_level<-rawdata$fr_levels

# prepare test data
testdata<-make_testdata(data)

# ======================================================================
# q_difficulty:f_relevance, fix f_entropy, level q_difficulty

# high
mod<- diff ~ qd_high + u_level + f_entropy + f_relevance + qd_high:f_entropy + qd_high:f_relevance + f_entropy:f_relevance + qd_high:f_entropy:f_relevance

input<-list(qd_high=qd_level$high, u_level=testdata[['u_level']],
        f_entropy=testdata[['fe_median']], f_relevance=testdata[['f_relevance']])

outputfile<-'data/lr_10_qxfr_high.txt'
model_train_predict(mod, data, input, outputfile)

# low
mod<- diff ~ qd_low + u_level + f_entropy + f_relevance + qd_low:f_entropy + qd_low:f_relevance + f_entropy:f_relevance + qd_low:f_entropy:f_relevance

input<-list(qd_low=qd_level$low, u_level=testdata[['u_level']],
        f_entropy=testdata[['fe_median']], f_relevance=testdata[['f_relevance']]) 

outputfile<-'data/lr_10_qxfr_low.txt'
model_train_predict(mod, data, input, outputfile)


# ========================================================================
# q_difficulty:f_entropy:f_relevance, level q_difficulty x f_relevance, vary f_entropy

# high x high
mod <- diff ~ qd_high + u_level + f_entropy + fr_high + qd_high:f_entropy + qd_high:fr_high + f_entropy:fr_high + qd_high:f_entropy:fr_high

input <- list(qd_high=qd_level$high, u_level=testdata[['u_level']],
        f_entropy=testdata[['f_entropy']], fr_high=fr_level$high)

outputfile<-'data/lr_10_qxfrxfe_hxh.txt'
model_train_predict(mod, data, input, outputfile)

# low x high
mod <- diff ~ qd_low + u_level + f_entropy + fr_high + qd_low:f_entropy + qd_low:fr_high + f_entropy:fr_high + qd_low:f_entropy:fr_high

input <- list(qd_low=qd_level$low, u_level=testdata[['u_level']],
        f_entropy=testdata[['f_entropy']], fr_high=fr_level$high)

outputfile<-'data/lr_10_qxfrxfe_lxh.txt'
model_train_predict(mod, data, input, outputfile)

# high x low
mod <- diff ~ qd_high + u_level + f_entropy + fr_low + qd_high:f_entropy + qd_high:fr_low + f_entropy:fr_low + qd_high:f_entropy:fr_low

input <- list(qd_high=qd_level$high, u_level=testdata[['u_level']],
        f_entropy=testdata[['f_entropy']], fr_low=fr_level$low)

outputfile<-'data/lr_10_qxfrxfe_hxl.txt'
model_train_predict(mod, data, input, outputfile)

# low x low
mod <- diff ~ qd_low + u_level + f_entropy + fr_low + qd_low:f_entropy + qd_low:fr_low + f_entropy:fr_low + qd_low:f_entropy:fr_low

input <- list(qd_low=qd_level$low, u_level=testdata[['u_level']],
        f_entropy=testdata[['f_entropy']], fr_low=fr_level$low)

outputfile<-'data/lr_10_qxfrxfe_lxl.txt'
model_train_predict(mod, data, input, outputfile)


# ============================================================
# Task all 
# data for test all 
rawdata<-prepare_data('data/smooth_data_task-1.csv')
data<-rawdata$data
qd_level<-rawdata$qd_levels
fe_level<-rawdata$fe_levels
fr_level<-rawdata$fr_levels

# prepare test data
testdata<-make_testdata(data)

#diff ~ u_level + f_relevance + q_difficulty + f_entropy + f_relevance:f_entropy + f_relevance:q_difficulty

# ============================================================
#f_relevance:f_entropy, level relevance, fix q_dfficulty



# ============================================================
#f_relevance:q_difficulty, fix entropy, level q_difficulty





