

X<-read.table("data/task_length_10.txt", header=TRUE)

 
e<-factor(X$e_lambda)
fp<-factor(X$f_prior)
fm<-factor(X$f_model)
qid<-factor(X$qid)
linm <-lm(X$effort~e+fp+fm+qid)

summary(linm)

metrics <- calc.relimp(linm, type = c("lmg", "pmvd", "first", "last", "betasq", "pratt" ))

lm_1 <-lm(X$effort~e+fp+fm)
summary(lm_1)
