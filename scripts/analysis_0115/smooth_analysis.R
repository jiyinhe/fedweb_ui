# load data
task1<-read.csv('data/smooth_data_task1.csv');
task10<-read.csv('data/smooth_data_task10.csv');
taskall<-read.csv('data/smooth_data_task-1.csv');


# user quality is categorical 
task1$u_level<-factor(task1$u_quality);
task10$u_level<-factor(task10$u_quality);
taskall$u_level<-factor(taskall$u_quality);

# fit the full model
#mylogit1 <- glm(diff ~ q_difficulty * u_level * f_entropy, data = task1, family = binomial(link="logit"))
#mylogit10 <- glm(diff ~ q_difficulty * u_level * f_entropy, data = task10, family = binomial(link="logit"))
#mylogitall <- glm(diff ~ q_difficulty * u_level * f_entropy, data = taskall, family = binomial(link="logit"))

# model selection
#search<-stepAIC(mylogit1)
#search$anova

#search<-stepAIC(mylogit10)
#search$anova

#search<-stepAIC(mylogitall)
#search$anova

# Fit the model again using the selected model
mylogit1 <- glm(diff ~ q_difficulty + u_level + f_entropy + q_difficulty:f_entropy + u_level:f_entropy, data=task1, family=binomial(link="logit"))
mylogit10 <- glm( diff ~ q_difficulty + u_level + f_entropy + q_difficulty:u_level + q_difficulty:f_entropy, data=task10, family=binomial(link="logit")) 
mylogitall <- glm(diff ~ q_difficulty + u_level + f_entropy + u_level:f_entropy, data=taskall, family=binomial(link="logit"))

# Generate prediction data for plot
# create X data points
# 4 u_levels
levels<-factor(c(0, 0.02, 0.1, 0.5))
# f_entropy between [c, d]
dfu<-seq(from=min(task1$f_entropy), to=max(task1$f_entropy), length.out=100)
# q_difficulty between [a, b], this is different per task
difficulty_1<-seq(from=min(task1$q_difficulty), to=max(task1$q_difficulty),length.out=100)
difficulty_10<-seq(from=min(task10$q_difficulty), to=max(task10$q_difficulty),length.out=100)
difficulty_all<-seq(from=min(taskall$q_difficulty), to=max(taskall$q_difficulty),length.out=100)

# make data as combinations of the 3 variables
data_task1<-expand.grid(difficulty_1, dfu, levels)
colnames(data_task1)<-c('q_difficulty', 'f_entropy', 'u_level')
data_task10<-expand.grid(difficulty_10, dfu, levels)
colnames(data_task10)<-c('q_difficulty', 'f_entropy', 'u_level')
data_taskall<-expand.grid(difficulty_all, dfu, levels)
colnames(data_taskall)<-c('q_difficulty', 'f_entropy', 'u_level')

# Get predicted data
# Data for q_difficulty x f_entropy
tmp1<-cbind(data_task1, predict(mylogit1, newdata=data_task1, type="link", se=TRUE))
newdata1<-within(tmp1, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

tmp10<-cbind(data_task10, predict(mylogit10, newdata=data_task10, type="link", se=TRUE))
newdata10<-within(tmp10, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

tmpall<-cbind(data_taskall, predict(mylogitall, newdata=data_taskall, type="link", se=TRUE))
newdataall<-within(tmpall, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

# save the data
write.table(newdata1, 'data/lr_3factor_1.txt')
write.table(newdata10, 'data/lr_3factor_10.txt')
write.table(newdataall, 'data/lr_3factor_all.txt')


# Data for f_entropy x u_level, take median of q_difficulty
data_task1<-expand.grid(median(task1$q_difficulty), dfu, levels)
colnames(data_task1)<-c('q_difficulty', 'f_entropy', 'u_level')
data_task10<-expand.grid(median(task10$q_difficulty), dfu, levels)
colnames(data_task10)<-c('q_difficulty', 'f_entropy', 'u_level')
data_taskall<-expand.grid(median(taskall$q_difficulty), dfu, levels)
colnames(data_taskall)<-c('q_difficulty', 'f_entropy', 'u_level')

tmp1<-cbind(data_task1, predict(mylogit1, newdata=data_task1, type="link", se=TRUE))
newdata1<-within(tmp1, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

tmp10<-cbind(data_task10, predict(mylogit10, newdata=data_task10, type="link", se=TRUE))
newdata10<-within(tmp10, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

tmpall<-cbind(data_taskall, predict(mylogitall, newdata=data_taskall, type="link", se=TRUE))
newdataall<-within(tmpall, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

# save the data
write.table(newdata1, 'data/lr_fxu_1.txt')
write.table(newdata10, 'data/lr_fxu_10.txt')
write.table(newdataall, 'data/lr_fxu_all.txt')

# Data for q_difficulty x u_level, take median of f_entropy
data_task1<-expand.grid(difficulty_1, median(task1$f_entropy), levels)
colnames(data_task1)<-c('q_difficulty', 'f_entropy', 'u_level')
data_task10<-expand.grid(difficulty_10, median(task10$f_entropy), levels)
colnames(data_task10)<-c('q_difficulty', 'f_entropy', 'u_level')
data_taskall<-expand.grid(difficulty_all, median(taskall$f_entropy), levels)
colnames(data_taskall)<-c('q_difficulty', 'f_entropy', 'u_level')


tmp1<-cbind(data_task1, predict(mylogit1, newdata=data_task1, type="link", se=TRUE))
newdata1<-within(tmp1, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

tmp10<-cbind(data_task10, predict(mylogit10, newdata=data_task10, type="link", se=TRUE))
newdata10<-within(tmp10, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

tmpall<-cbind(data_taskall, predict(mylogitall, newdata=data_taskall, type="link", se=TRUE))
newdataall<-within(tmpall, {
    predictedProb<-plogis(fit) 
    LL<-plogis(fit-(1.96*se.fit))
    UL<-plogis(fit+(1.96*se.fit))
})

# save the data
write.table(newdata1, 'data/lr_qxu_1.txt')
write.table(newdata10, 'data/lr_qxu_10.txt')
write.table(newdataall, 'data/lr_qxu_all.txt')






