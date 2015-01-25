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
difficulty_1<-seq(from=min(task1$q_difficulty),
to=max(task1$q_difficulty),length.out=100)
difficulty_10<-seq(from=min(task10$q_difficulty),
to=max(task10$q_difficulty),length.out=100)
difficulty_all<-seq(from=min(taskall$q_difficulty),
to=max(taskall$q_difficulty),length.out=100)

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

# retrain the model to seperate two levels of difficulty
# recenter q_difficulty to two levels: high & low around 0
task1$qd_high<-task1$q_difficulty - (mean(task1$q_difficulty)+sd(task1$q_difficulty))
task1$qd_low<-task1$q_difficulty - (mean(task1$q_difficulty)-sd(task1$q_difficulty))
# retrain the model to get coefficient of f_entropy at different levels of
# q_difficulty
summary(model1)
select1.mod_high<-diff ~ qd_high + u_level + f_entropy + qd_high:u_level + qd_high:f_entropy
model1.high<-(glm(select1.mod_high, data=task1, family=binomial(link = logit)))
summary(model1.high)

select1.mod_low<-diff ~ qd_low + u_level + f_entropy + qd_low:u_level + qd_low:f_entropy
model1.low<-(glm(select1.mod_low, data=task1, family=binomial(link = logit)))
summary(model1.low)

# predicted prob with high and low models
data_high<-expand.
data<-expand.grid(difficulty_1, levels, entropy, median(task1$f_relevance))
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'f_relevance')

# model predict
tmp<-cbind(data, predict(model1, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})
write.table(newdata, 'data/lr_1_qxfe.txt')



# Task 10
# q_difficulty x f_relevance; fix f_entropy, keep u_levels
data<-expand.grid(difficulty_10, levels, median(task10$f_entropy), relevance)
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'f_relevance')

# model predict
tmp<-cbind(data, predict(model10, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

write.table(newdata, 'data/lr_10_qxfr.txt')



# q_difficulty x f_entropy x f_relevance ; keep u_level
data<-expand.grid(difficulty_10, levels, entropy, relevance)

colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'f_relevance')

# model predict with model 10
tmp<-cbind(data, predict(model10, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

write.table(newdata, 'data/lr_10_4factors.txt')



# Task all
# f_entropy x f_relevance; fix difficulty, keep u_level
data<-expand.grid(median(taskall$q_difficulty), levels, entropy, relevance)
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'f_relevance')

# model predict with model all
tmp<-cbind(data, predict(modelall, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

write.table(newdata, 'data/lr_all_fexfr.txt')

# q_difficulty x f_relevance; fix f_entropy, keep u_level
data<-expand.grid(difficulty_all, levels, median(taskall$f_entropy), relevance)
colnames(data)<-c('q_difficulty', 'u_level', 'f_entropy', 'f_relevance')

# model predict
tmp<-cbind(data, predict(modelall, newdata=data, type="link", se=TRUE))
newdata<-within(tmp, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

write.table(newdata, 'data/lr_all_qxfr.txt')


