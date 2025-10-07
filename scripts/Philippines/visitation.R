library(ggplot2)
library(ggpubr)

setwd("C:/Users/jgldstn/Documents/GEF/Philippines/visitation/")
mean <- read.csv("visitation_mean_2005_2017.csv")

# natural log +1 regression of nationwide visits vs. PUDs

ln_meanPUD <- log1p(mean$PUD_mean)
ln_meanTotal <- log1p(mean$meanTotal)

fit <- lm(ln_meanTotal ~ ln_meanPUD, mean)
fit

summary(fit)

ggplot(fit, aes(x = ln_meanPUD, y = ln_meanTotal)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 7, label.y = 13.5) +
  stat_cor(aes(label=..rr.label..), label.x = 8, label.y = 13.5) +
  labs(title = "Mean total annual visitors vs. mean annual PUDs by PHI regions, 2005-2017") +
  xlab("ln(mean annual PUDs + 1)") +
  ylab("ln(mean total annual visitors + 1)")

# 2005-2013
ln_mean2013PUD <- log1p(mean$PUD_mean2005_2013)
ln_mean2013Total <- log1p(mean$meanTotal2005_2013)

fit2013 <- lm(ln_mean2013Total ~ ln_mean2013PUD, mean)
fit2013

summary(fit2013)

ggplot(fit2013, aes(x = ln_mean2013PUD, y = ln_mean2013Total)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 7, label.y = 13.5) +
  stat_cor(aes(label=..rr.label..), label.x = 8, label.y = 13.5) +
  labs(title = "Mean total annual visitors vs. mean annual PUDs for PHI regions, 2005-2013") +
  xlab("ln(mean annual PUDs + 1)") +
  ylab("ln(mean total annual visitors + 1)")

#####################################
# regression of Foreign visits vs. PUDs

ln_meanForeign <- log1p(mean$meanForeign)

fitForeign <- lm(ln_meanForeign ~ ln_meanPUD, mean)
fitForeign

summary(fitForeign)

ggplot(fitForeign, aes(x = ln_meanPUD, y = ln_meanForeign)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 7, label.y = 10.5) +
  stat_cor(aes(label=..rr.label..), label.x = 7.6, label.y = 10.5) +
  labs(title = "Mean foreign annual visitors vs. mean annual PUDs for PHI regions, 2005-2017") +
  xlab("ln(mean annual PUDs + 1)") +
  ylab("ln(mean annual foreign visitors + 1)")

# 2005-2013
ln_mean2013Foreign <- log1p(mean$meanForeign2005_2013)

fit2013Foreign <- lm(ln_mean2013Foreign ~ ln_mean2013PUD, mean)
fit2013Foreign

summary(fit2013Foreign)

ggplot(fit2013Foreign, aes(x = ln_mean2013PUD, y = ln_mean2013Foreign)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 7, label.y = 10) +
  stat_cor(aes(label=..rr.label..), label.x = 8, label.y = 10) +
  labs(title = "Mean foreign annual visitors vs. mean annual PUDs for PHI regions, 2005-2013") +
  xlab("ln(mean annual PUDs + 1)") +
  ylab("ln(mean annual foreign visitors + 1)")

#####################################
# regression of Domestic visits vs. PUDs

ln_meanDomestic <- log1p(mean$meanDomestic)

fitDomestic <- lm(ln_meanDomestic ~ ln_meanPUD, mean)
fitDomestic

summary(fitDomestic)

ggplot(fitDomestic, aes(x = ln_meanPUD, y = ln_meanDomestic)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 7, label.y = 13) +
  stat_cor(aes(label=..rr.label..), label.x = 8, label.y = 13) +
  labs(title = "Mean domestic annual visitors vs. mean annual PUDs for PHI regions, 2005-2017") +
  xlab("ln(mean annual PUDs + 1)") +
  ylab("ln(mean annual domestic visitors + 1)")

#######################################################
# regression of nationwide visits vs. eBird CUDs

ln_meanCUD <- log1p(mean$CUD_mean)
ln_meanTotal <- log1p(mean$meanTotal)

fit_eBird <- lm(ln_meanTotal ~ ln_meanCUD, mean)
fit_eBird

summary(fit_eBird)

ggplot(fit_eBird, aes(x = ln_meanCUD, y = ln_meanTotal)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 4, label.y = 13) +
  stat_cor(aes(label=..rr.label..), label.x = 5, label.y = 13) +
  labs(title = "Mean total annual visitors vs. mean annual eBird CUDs for PHI regions, 2005-2017") +
  xlab("ln(mean annual CUDs + 1)") +
  ylab("ln(mean total annual visitors + 1)")

#######################################################
# regression of foreign visits vs. eBird CUDs

ln_meanForeign <- log1p(mean$meanForeign)

fit_eBird_foreign <- lm(ln_meanForeign ~ ln_meanCUD, mean)
fit_eBird_foreign

summary(fit_eBird_foreign)

ggplot(fit_eBird_foreign, aes(x = ln_meanCUD, y = ln_meanForeign)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 4, label.y = 9.5) +
  stat_cor(aes(label=..rr.label..), label.x = 5, label.y = 9.5) +
  labs(title = "Mean foreign annual visitors vs. mean annual eBird CUDs for PHI regions, 2005-2017") +
  xlab("ln(mean annual CUDs + 1)") +
  ylab("ln(mean foreign annual visitors + 1)")

##########################################################
# regression of nationwide vists vs. Flickr PUDs + eBird CUDs

ln_meanPUD_CUD <- log1p(mean$PUD_CUD_mean)
ln_meanTotal <- log1p(mean$meanTotal)

fit_Flickr_eBird <- lm(ln_meanTotal ~ ln_meanPUD_CUD, mean)
fit_Flickr_eBird

summary(fit_Flickr_eBird)

ggplot(fit_Flickr_eBird, aes(x = ln_meanPUD_CUD, y = ln_meanTotal)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 7, label.y = 13.5) +
  stat_cor(aes(label=..rr.label..), label.x = 8, label.y = 13.5) +
  labs(title = "Mean total annual visitors vs. mean annual Flcikr + eBird by PHI region, 2005-2017") +
  xlab("ln(mean annual PUDs and CUDs + 1)") +
  ylab("ln(mean total annual visitors + 1)")

##########################################################
# regression of foreign vists vs. Flickr PUDs + eBird CUDs

ln_meanPUD_CUD <- log1p(mean$PUD_CUD_mean)
ln_meanForeign <- log1p(mean$meanForeign)

fit_Flickr_eBird_foreign <- lm(ln_meanForeign ~ ln_meanPUD_CUD, mean)
fit_Flickr_eBird_foreign

summary(fit_Flickr_eBird_foreign)

ggplot(fit_Flickr_eBird_foreign, aes(x = ln_meanPUD_CUD, y = ln_meanForeign)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 7, label.y = 11) +
  stat_cor(aes(label=..rr.label..), label.x = 8, label.y = 11) +
  labs(title = "Mean foreign annual visitors vs. mean annual Flcikr + eBird by PHI region, 2005-2017") +
  xlab("ln(mean annual PUDs and CUDs + 1)") +
  ylab("ln(mean foreign annual visitors + 1)")

##########################################################
# total visitation trends X region, 2005-2017

totalTrends <- read.csv("totalVisitationTrend_X_PHI_region_2005_2007.csv")

#regional
plot(totalTrends$year, totalTrends$CAR, type="l", main = "annual visits by region", ylim=c(0, 7150000), xlab = "year", ylab = "annual visits")
lines(totalTrends$year, totalTrends$II,lty=1)
lines(totalTrends$year, totalTrends$III,lty=1)
#lines(totalTrends$year, totalTrends$IV,lty=1)
lines(totalTrends$year, totalTrends$V,lty=1)
lines(totalTrends$year, totalTrends$VI,lty=1)
lines(totalTrends$year, totalTrends$VII,lty=1)
lines(totalTrends$year, totalTrends$VIII,lty=1)
lines(totalTrends$year, totalTrends$IX,lty=1)
lines(totalTrends$year, totalTrends$X,lty=1)
lines(totalTrends$year, totalTrends$XI,lty=1)
lines(totalTrends$year, totalTrends$XII,lty=1)
lines(totalTrends$year, totalTrends$XIII,lty=1)
#lines(totalTrends$year, totalTrends$NCR,lty=1)
lines(totalTrends$year, totalTrends$I,lty=1)

#national
plot(totalTrends$year, totalTrends$NATIONAL, type="l", main = "nationwide annual visits", ylim=c(0, 47100000), xlab = "year", ylab = "annual visits")
lines(totalTrends$year, totalTrends$NATIONAL,lty=1)

#######################################################
# Region I

r1 <- read.csv("Region_I_visitation_2005_2017.csv")

ln_PUD <- log1p(r1$PUD_Region1_total)
ln_total <- log1p(r1$Total)

fit_r1 <- lm(ln_total ~ ln_PUD, r1)
fit_r1

summary(fit_r1)

ggplot(fit_r1, aes(x = ln_PUD, y = ln_total)) +
  geom_point() +
  stat_smooth(method = "lm", col = "blue") +
  stat_regline_equation(label.x = 5, label.y = 11.5) +
  stat_cor(aes(label=..rr.label..), label.x = 5.5, label.y = 11.5) +
  labs(title = "PHI Region I (2005-2017)") +
  xlab("ln(annual PUDs + 1)") +
  ylab("ln(total annual visitors + 1)")

#############################################################
# timeseries

library(scales)

timeseries <- read.csv("PUDs_visits_2005_2017.csv")

ggplot(timeseries, aes(x=Year)) +
  geom_line(aes(y=Total), color="purple") +
  geom_line(aes(y=Foreign), color="red") +
  geom_line(aes(y=Domestic), color="blue") +
  geom_line(aes(y=PUD_total*2000), color="black") +
  scale_y_continuous(name = "visitor-days", sec.axis = sec_axis(trans = ~./2000, name = "PUDs")) +
  scale_x_continuous(breaks = pretty_breaks())

#legend
names <- c('Total', 'Foreign', 'Domestic', 'PUDs')
clrs <- c('purple', 'red', 'blue', 'black')
ltype <- c(1, 1)
plot(NULL ,xaxt = 'n',yaxt='n',bty='n',ylab='',xlab='', xlim = 0:1, ylim = 0:1)
lgnd <- legend("topleft", title = "", legend = names, lty=ltype, lwd = 3, cex = 3,
               bty='n', col = clrs)
###################################################
library("tidyverse")

PUD <- timeseries$PUD_total*2000

df <- timeseries %>%
  select(Year, Total, Foreign, Domestic, PUD) %>%
  gather(key = "variable", value = "value", -Year)
head(df)


