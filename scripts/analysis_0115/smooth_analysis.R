# load data
task1<-read.csv('data/smooth_data_task1.csv');
task10<-read.csv('data/smooth_data_task10.csv');
taskall<-read.csv('data/smooth_data_task-1.csv');



# user quality is categorical 
task1$u_level<-factor(task1$u_quality);
task10$u_level<-factor(task10$u_quality);
taskall$u_level<-factor(taskall$u_quality);

# fit the full model
mylogit1 <- glm(diff ~ q_difficulty * u_level * f_entropy, data = task1, family = binomial(link="logit"))
mylogit10 <- glm(diff ~ q_difficulty * u_level * f_entropy, data = task10, family = binomial(link="logit"))
mylogitall <- glm(diff ~ q_difficulty * u_level * f_entropy, data = taskall, family = binomial(link="logit"))

# model selection
search<-stepAIC(mylogit1)
search$anova

search<-stepAIC(mylogit10)
search$anova

search<-stepAIC(mylogitall)
search$anova

# Fit the model again using the selected model
mylogit1 <- glm(diff ~ q_difficulty + u_level + f_entropy + q_difficulty:f_entropy + u_level:f_entropy, data=task1, family=binomial(link="logit"))
mylogit10 <- glm( diff ~ q_difficulty + u_level + f_entropy + q_difficulty:u_level + q_difficulty:f_entropy, data=task10, family=binomial(link="logit")) 
mylogitall <- glm(diff ~ q_difficulty + u_level + f_entropy + u_level:f_entropy, data=taskall, family=binomial(link="logit"))


