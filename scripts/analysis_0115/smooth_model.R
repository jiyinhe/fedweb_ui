# load data
task1<-read.csv('data/smooth_data_task1.csv');
task10<-read.csv('data/smooth_data_task10.csv');
taskall<-read.csv('data/smooth_data_task-1.csv');


# user quality is categorical 
task1$u_level<-factor(task1$u_quality);
task10$u_level<-factor(task10$u_quality);
taskall$u_level<-factor(taskall$u_quality);


#empty models
empty1.mod<- glm(formula = diff ~ 1, family = binomial(link = logit), data = task1)
empty10.mod<- glm(formula = diff ~ 1, family = binomial(link = logit), data = task10)
emptyall.mod<- glm(formula = diff ~ 1, family = binomial(link = logit), data = taskall)



# fit the full model
full1.mod<-glm(diff ~ q_difficulty * u_level * f_entropy * f_relevance, data = task1, family = binomial(link="logit"))
full10.mod<-glm(diff ~ q_difficulty * u_level * f_entropy * f_relevance, data = task10, family = binomial(link="logit"))
fullall.mod<-glm(diff ~ q_difficulty * u_level * f_entropy * f_relevance, data = taskall, family = binomial(link="logit"))



# model selection
# find 1
search1.f <- stepAIC(object = empty1.mod, scope = list(upper = full1.mod), direction = "forward", k = log(nrow(task1)), trace = TRUE)
search1.f$anova

search1.b <- stepAIC(object = full1.mod, scope = list(lower = empty1.mod), direction = "backward", k = log(nrow(task1)), trace = TRUE)
search1.b$anova

# selected model:
select1.mod<-diff ~ q_difficulty + u_level + f_entropy + q_difficulty:u_level + q_difficulty:f_entropy
#select1.mod <- diff ~ q_difficulty + u_level + f_entropy + q_difficulty:u_level + q_difficulty:f_entropy
model1<-(glm(select1.mod, data=task1, family=binomial(link = logit)))

# find 10
search10.f <- stepAIC(object = empty10.mod, scope = list(upper = full10.mod),
direction = "both", k = log(nrow(task10)), trace = TRUE)
search10.f$anova

search10.b <- stepAIC(object = full10.mod, scope = list(lower = empty10.mod), direction = "backward", k = log(nrow(task10)), trace = TRUE)
search10.b$anova

# selected model
#select10.mod <- diff ~ q_difficulty + u_level + f_relevance + q_difficulty:f_relevance
select10.mod<-diff ~ q_difficulty + u_level + f_entropy + f_relevance + q_difficulty:f_entropy + q_difficulty:f_relevance + f_entropy:f_relevance + q_difficulty:f_entropy:f_relevance

model10<-(glm(select10.mod, data=task10, family=binomial(link = logit)))

# find all
searchall.f <- stepAIC(object = emptyall.mod, scope = list(upper = fullall.mod),
direction = "backward", k = log(nrow(taskall)), trace = TRUE)
searchall.f$anova

searchall.b <- stepAIC(object = fullall.mod, scope = list(lower = emptyall.mod),
direction = "backward", k = log(nrow(taskall)), trace = TRUE)
searchall.b$anova

# selected model
#selectall.mod <- diff ~ u_level + f_relevance + q_difficulty + f_entropy + f_relevance:f_entropy + f_relevance:q_difficulty
selectall.mode <- diff ~ u_level + f_relevance + q_difficulty + f_entropy + f_relevance:f_entropy + f_relevance:q_difficulty
modelall<-(glm(selectall.mod, data=taskall, family=binomial(link = logit)))


