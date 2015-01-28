# load data
task1<-read.csv('data/smooth_data_task1.csv');
task10<-read.csv('data/smooth_data_task10.csv');
taskall<-read.csv('data/smooth_data_task-1.csv');


# user quality is categorical 
task1$u_level<-factor(task1$u_quality);
task10$u_level<-factor(task10$u_quality);
taskall$u_level<-factor(taskall$u_quality);

# Fit the model again using the selected model
# model 1
select1.mod<-diff ~ q_difficulty + u_level + f_entropy + q_difficulty:u_level + q_difficulty:f_entropy
model1<-(glm(select1.mod, data=task1, family=binomial(link = logit)))

# model 10
select10.mod<-diff ~ q_difficulty + u_level + f_entropy + f_relevance + q_difficulty:f_entropy + q_difficulty:f_relevance + f_entropy:f_relevance + q_difficulty:f_entropy:f_relevance
model10<-(glm(select10.mod, data=task10, family=binomial(link = logit)))

# model all
selectall.mode <- diff ~ u_level + f_relevance + q_difficulty + f_entropy + f_relevance:f_entropy + f_relevance:q_difficulty
modelall<-(glm(selectall.mod, data=taskall, family=binomial(link = logit)))


# Generate prediction data for plot
# create X data points
# 4 u_levels
levels<-factor(c(0, 0.1, 0.5, 1))
# f_entropy between [c, d]
entropy<-seq(from=min(task1$f_entropy), to=max(task1$f_entropy), length.out=100)
# f_relevance 
relevance<-seq(from=min(task1$f_relevance), to=max(task1$f_relevance), length.out=100)

# q_difficulty between [a, b], this is different per task
difficulty_1<-seq(from=min(task1$q_difficulty), to=max(task1$q_difficulty),length.out=100)
difficulty_10<-seq(from=min(task10$q_difficulty), to=max(task10$q_difficulty),length.out=100)
difficulty_all<-seq(from=min(taskall$q_difficulty), to=max(taskall$q_difficulty),length.out=100)

# Make data for plots -- only consider interactions that were significant
# Task 1
# q_difficulty x u_level;  fix f_entropy, f_relevance
data<-expand.grid(difficulty_1, levels, median(task1$f_entropy),median(task1$f_relevance))
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'f_relevance')

# model predict
tmp<-cbind(data, predict(model1, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_1_qxu.txt')


# q_difficulty x f_entropy; fix f_relevance, keep u_levels
# retrain the model to seperate three levels of difficulty
high<-quantile(task1$q_difficulty, 0.75)
mid<-quantile(task1$q_difficulty, 0.5)
low<-quantile(task1$q_difficulty, 0.25)

task1$qd_high<-task1$q_difficulty - high
task1$qd_mid<-task1$q_difficulty - mid
task1$qd_low<-task1$q_difficulty - low

# retrain the model to get coefficient of f_entropy at different levels of
# q_difficulty
select1.mod_high<-diff ~ qd_high + u_level + f_entropy + qd_high:u_level + qd_high:f_entropy
model1.high<-(glm(select1.mod_high, data=task1, family=binomial(link = logit)))

select1.mod_mid<-diff ~ qd_mid + u_level + f_entropy + qd_mid:u_level + qd_mid:f_entropy
model1.mid<-(glm(select1.mod_mid, data=task1, family=binomial(link = logit)))

select1.mod_low<-diff ~ qd_low + u_level + f_entropy + qd_low:u_level + qd_low:f_entropy
model1.low<-(glm(select1.mod_low, data=task1, family=binomial(link = logit)))

# predicted prob with high and low models, 
# q_difficulty fixed at 3 levels, fix  relevance
data_high<-expand.grid(high, levels, entropy, median(task1$f_relevance))
data_mid<-expand.grid(mid, levels, entropy, median(task1$f_relevance))
data_low<-expand.grid(low, levels, entropy, median(task1$f_relevance))
#data<-expand.grid(difficulty_1, levels, entropy, median(task1$f_relevance))
colnames(data_high)<-c('qd_high', 'u_level', 'f_entropy', 'f_relevance')
colnames(data_mid)<-c('qd_mid', 'u_level', 'f_entropy', 'f_relevance')
colnames(data_low)<-c('qd_low', 'u_level', 'f_entropy', 'f_relevance')

# model predict
# qd = high
tmp<-cbind(data_high, predict(model1.high, newdata=data_high, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_1_qxfe_high.txt')

# qd = mid 
tmp<-cbind(data_mid, predict(model1.mid, newdata=data_mid, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_1_qxfe_mid.txt')


# qd = low
tmp<-cbind(data_low, predict(model1.low, newdata=data_low, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_1_qxfe_low.txt')


# Task 10
# q_difficulty x f_relevance; fix f_entropy, keep u_levels
# make q_difficulty 3 levels
high<-quantile(task10$q_difficulty, 0.75)
mid<-quantile(task10$q_difficulty, 0.5)
low<-quantile(task10$q_difficulty, 0.25)

task10$qd_high<-task10$q_difficulty - high
task10$qd_mid<-task10$q_difficulty - mid
task10$qd_low<-task10$q_difficulty - low

# Retrain the models for three levels
# high
select10.mod_high<-diff ~ qd_high + u_level + f_entropy + f_relevance + qd_high:f_entropy + qd_high:f_relevance + f_entropy:f_relevance + qd_high:f_entropy:f_relevance
model10.high<-(glm(select10.mod_high, data=task10, family=binomial(link = logit)))

#mid
select10.mod_mid<-diff ~ qd_mid + u_level + f_entropy + f_relevance +
qd_mid:f_entropy + qd_mid:f_relevance + f_entropy:f_relevance + qd_mid:f_entropy:f_relevance
model10.mid<-(glm(select10.mod_mid, data=task10, family=binomial(link = logit)))

#low
select10.mod_low<-diff ~ qd_low + u_level + f_entropy + f_relevance +
qd_low:f_entropy + qd_low:f_relevance + f_entropy:f_relevance + qd_low:f_entropy:f_relevance
model10.low<-(glm(select10.mod_low, data=task10, family=binomial(link = logit)))

# Re-run the prediciton
# Fix entropy, fix difficulty at 3 levels, vary relevance
# high
data<-expand.grid(high, levels, median(task10$f_entropy), relevance)
colnames(data)<-c('qd_high', 'u_level', 'f_entropy', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfr_high.txt')

# mid
data<-expand.grid(mid, levels, median(task10$f_entropy), relevance)
colnames(data)<-c('qd_mid', 'u_level', 'f_entropy', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.mid, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfr_mid.txt')

# low
data<-expand.grid(low, levels, median(task10$f_entropy), relevance)
colnames(data)<-c('qd_low', 'u_level', 'f_entropy', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfr_low.txt')


# q_difficulty x f_entropy x f_relevance ; keep u_level
# use the same division for q_difficulty
# create high and low entropy level
high_e<-mean(task10$f_entropy)+sd(task10$f_entropy)
low_e<-mean(task10$f_entropy)-sd(task10$f_entropy)
mid_e<-mean(task10$f_entropy)

task10$fe_high<-task10$f_entropy - high_e
task10$fe_mid<-task10$f_entropy - mid_e
task10$fe_low<-task10$f_entropy - low_e

# A relevance version
high_r<-mean(task10$f_relevance)+sd(task10$f_relevance)
low_r<-mean(task10$f_relevance)-sd(task10$f_relevance)
mid_r<-mean(task10$f_relevance)

task10$fr_high<-task10$f_relevance - high_r
task10$fr_mid<-task10$f_relevance - mid_r
task10$fr_low<-task10$f_relevance - low_r


# qd_high x fe_high
# retrain the models
# qd_high x fe_high x relevance
mod<-diff ~ qd_high + u_level + fe_high + f_relevance + qd_high:fe_high + qd_high:f_relevance + fe_high:f_relevance + qd_high:fe_high:f_relevance
model10.high_high<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(high, levels, high_e, relevance)
colnames(data)<-c('qd_high', 'u_level', 'fe_high', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.high_high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_hxh.txt')

# A relevance version
# retrain the models
# qd_high x fr_high x entropy
mod<-diff ~ qd_high + u_level + fr_high + f_entropy + qd_high:fr_high + qd_high:f_entropy + fr_high:f_entropy + qd_high:fr_high:f_entropy
model10.high_high<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_relevance at its levels, vary entropy
data<-expand.grid(high, levels, entropy, high_r)
colnames(data)<-c('qd_high', 'u_level', 'f_entropy', 'fr_high')
# model predict
tmp<-cbind(data, predict(model10.high_high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfrxfe_hxh.txt')


# qd_mid x fe_high
# retrain the models
# qd_mid x fe_high x relevance
mod<-diff ~ qd_mid + u_level + fe_high + f_relevance + qd_mid:fe_high + qd_mid:f_relevance + fe_high:f_relevance + qd_mid:fe_high:f_relevance
model10.mid_high<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(mid, levels, high_e, relevance)
colnames(data)<-c('qd_mid', 'u_level', 'fe_high', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.mid_high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_mxh.txt')

# A relevance version
# retrain the models
# qd_mid x fr_high x entropy
mod<-diff ~ qd_mid + u_level + fr_high + f_entropy + qd_mid:fr_high + qd_mid:f_entropy + fr_high:f_entropy + qd_mid:fr_high:f_entropy
model10.mid_high<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_relevance at its levels, vary entropy
data<-expand.grid(mid, levels, entropy, high_r)
colnames(data)<-c('qd_mid', 'u_level', 'f_entropy', 'fr_high')
# model predict
tmp<-cbind(data, predict(model10.mid_high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfrxfe_mxh.txt')

# qd_low x fe_high
# retrain the models
# qd_low x fe_high x relevance
mod<-diff ~ qd_low + u_level + fe_high + f_relevance + qd_low:fe_high + qd_low:f_relevance + fe_high:f_relevance + qd_low:fe_high:f_relevance
model10.low_high<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(low, levels, high_e, relevance)
colnames(data)<-c('qd_low', 'u_level', 'fe_high', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.low_high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_lxh.txt')


# A relevance version
# retrain the models
# qd_low x fr_high x entropy
mod<-diff ~ qd_low + u_level + fr_high + f_entropy + qd_low:fr_high + qd_low:f_entropy + fr_high:f_entropy + qd_low:fr_high:f_entropy
model10.low_high<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_relevance at its levels, vary entropy
data<-expand.grid(low, levels, entropy, high_r)
colnames(data)<-c('qd_low', 'u_level', 'f_entropy', 'fr_high')
# model predict
tmp<-cbind(data, predict(model10.low_high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfrxfe_lxh.txt')


# qd_high x fe_mid
# retrain the models
# qd_high x fe_mid x relevance
mod<-diff ~ qd_high + u_level + fe_mid + f_relevance + qd_high:fe_mid + qd_high:f_relevance + fe_mid:f_relevance + qd_high:fe_mid:f_relevance
model10.high_mid<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(high, levels, mid_e, relevance)
colnames(data)<-c('qd_high', 'u_level', 'fe_mid', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.high_mid, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_hxm.txt')


# qd_mid x fe_mid
# retrain the models
# qd_mid x fe_mid x relevance
mod<-diff ~ qd_mid + u_level + fe_mid + f_relevance + qd_mid:fe_mid + qd_mid:f_relevance + fe_mid:f_relevance + qd_mid:fe_mid:f_relevance
model10.mid_mid<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(mid, levels, mid_e, relevance)
colnames(data)<-c('qd_mid', 'u_level', 'fe_mid', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.mid_mid, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_mxm.txt')

# qd_low x fe_mid
# retrain the models
# qd_low x fe_mid x relevance
mod<-diff ~ qd_low + u_level + fe_mid + f_relevance + qd_low:fe_mid + qd_low:f_relevance + fe_mid:f_relevance + qd_low:fe_mid:f_relevance
model10.low_mid<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(low, levels, mid_e, relevance)
colnames(data)<-c('qd_low', 'u_level', 'fe_mid', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.low_mid, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_lxm.txt')

# qd_high x fe_low
# retrain the models
# qd_high x fe_low x relevance
mod<-diff ~ qd_high + u_level + fe_low + f_relevance + qd_high:fe_low + qd_high:f_relevance + fe_low:f_relevance + qd_high:fe_low:f_relevance
model10.high_low<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(high, levels, low_e, relevance)
colnames(data)<-c('qd_high', 'u_level', 'fe_low', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.high_low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_hxl.txt')

# A relevance version
# retrain the models
# qd_high x fr_low x entropy
mod<-diff ~ qd_high + u_level + fr_low + f_entropy + qd_high:fr_low + qd_high:f_entropy + fr_low:f_entropy + qd_high:fr_low:f_entropy
model10.high_low<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_relevance at its levels, vary entropy
data<-expand.grid(high, levels, entropy, low_r)
colnames(data)<-c('qd_high', 'u_level', 'f_entropy', 'fr_low')
# model predict
tmp<-cbind(data, predict(model10.high_low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfrxfe_hxl.txt')



# qd_mid x fe_low
# retrain the models
# qd_mid x fe_low x relevance
mod<-diff ~ qd_mid + u_level + fe_low + f_relevance + qd_mid:fe_low + qd_mid:f_relevance + fe_low:f_relevance + qd_mid:fe_low:f_relevance
model10.mid_low<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(mid, levels, low_e, relevance)
colnames(data)<-c('qd_mid', 'u_level', 'fe_low', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.mid_low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_mxl.txt')

# qd_low x fe_low
# retrain the models
# qd_low x fe_low x relevance
mod<-diff ~ qd_low + u_level + fe_low + f_relevance + qd_low:fe_low + qd_low:f_relevance + fe_low:f_relevance + qd_low:fe_low:f_relevance
model10.low_low<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_entropy at its levels, vary relevance
data<-expand.grid(low, levels, low_e, relevance)
colnames(data)<-c('qd_low', 'u_level', 'fe_low', 'f_relevance')
# model predict
tmp<-cbind(data, predict(model10.low_low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfexfr_lxl.txt')

# A relevance version
# retrain the models
# qd_low x fr_low x entropy
mod<-diff ~ qd_low + u_level + fr_low + f_entropy + qd_low:fr_low + qd_low:f_entropy + fr_low:f_entropy + qd_low:fr_low:f_entropy
model10.low_low<-(glm(mod, data=task10, family=binomial(link = logit)))

# predict, fix q_difficulty, f_relevance at its levels, vary entropy
data<-expand.grid(low, levels, entropy, low_r)
colnames(data)<-c('qd_low', 'u_level', 'f_entropy', 'fr_low')
# model predict
tmp<-cbind(data, predict(model10.low_low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_10_qxfrxfe_lxl.txt')


# Task all
# f_entropy x f_relevance; fix difficulty, keep u_level
# retrain the model to seperate three levels of f_relevance
high_r<-quantile(taskall$f_relevance, 0.75)
mid_r<-quantile(taskall$f_relevance, 0.5)
low_r<-quantile(taskall$f_relevance, 0.25)

taskall$fr_high<-task1$q_difficulty - high_r
taskall$fr_low<-task1$q_difficulty - low_r

# Retrain the model
mod <- diff ~ u_level + fr_high + q_difficulty + f_entropy + fr_high:f_entropy + fr_high:q_difficulty
modelall.high<-(glm(mod, data=taskall, family=binomial(link = logit)))

# fix q_difficulty, set f_relevance to its level, vary entropy
data<-expand.grid(median(taskall$q_difficulty), levels, entropy, high_r)
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'fr_high')

# model predict with model all
tmp<-cbind(data, predict(modelall.high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

write.table(newdata, 'data/lr_all_frxfe_high.txt')

# Retrain the model
mod <- diff ~ u_level + fr_low + q_difficulty + f_entropy + fr_low:f_entropy + fr_low:q_difficulty
modelall.low<-(glm(mod, data=taskall, family=binomial(link = logit)))

# fix q_difficulty, set f_relevance to its level, vary entropy
data<-expand.grid(median(taskall$q_difficulty), levels, entropy, low_r)
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'fr_low')

# model predict with model all
tmp<-cbind(data, predict(modelall.low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

write.table(newdata, 'data/lr_all_frxfe_low.txt')


# q_difficulty x f_relevance; fix f_entropy, keep u_level
high<-quantile(taskall$q_difficulty, 0.75)
low<-quantile(taskall$q_difficulty, 0.25)

taskall$qd_high<-task1$q_difficulty - high
taskall$qd_low<-task1$q_difficulty - low

# retrain the model
#mod <- diff ~ u_level + f_relevance + qd_high + f_entropy + f_relevance:f_entropy + f_relevance:qd_high
#modelall.high<-(glm(mod, data=taskall, family=binomial(link = logit)))
mod <- diff ~ u_level + fr_high + q_difficulty + f_entropy + fr_high:f_entropy + fr_high:q_difficulty
modelall.high<-(glm(mod, data=taskall, family=binomial(link = logit)))

# Fix f_entropy, set q_difficulty to its level, vary relevance
#data<-expand.grid(high, levels, median(taskall$f_entropy), relevance)
#colnames(data)<-c('qd_high', 'u_level', 'f_entropy', 'f_relevance')
data<-expand.grid(difficulty_all, levels, median(taskall$f_entropy), high_r)
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'fr_high')

# model predict
tmp<-cbind(data, predict(modelall.high, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

write.table(newdata, 'data/lr_all_frxq_high.txt')

# retrain the model
#mod <- diff ~ u_level + f_relevance + qd_low + f_entropy + f_relevance:f_entropy + f_relevance:qd_low
#modelall.low<-(glm(mod, data=taskall, family=binomial(link = logit)))
mod <- diff ~ u_level + fr_low + q_difficulty + f_entropy + fr_low:f_entropy + fr_low:q_difficulty
modelall.low<-(glm(mod, data=taskall, family=binomial(link = logit)))


# Fix f_entropy, set q_difficulty to its level, vary relevance
#data<-expand.grid(low, levels, median(taskall$f_entropy), relevance)
#colnames(data)<-c('qd_low', 'u_level', 'f_entropy', 'f_relevance')
data<-expand.grid(difficulty_all, levels, median(taskall$f_entropy), low_r)
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'fr_low')


# model predict
tmp<-cbind(data, predict(modelall.low, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

#write.table(newdata, 'data/lr_all_qxfr_low.txt')
write.table(newdata, 'data/lr_all_frxq_low.txt')



