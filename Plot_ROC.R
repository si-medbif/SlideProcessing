library(tidyverse)
library(cowplot)
library(pROC)
library(imager)
library(reshape2)



#Specify input/output here
source_dir <- "/path/to/prediction_directory"
out_dir <- "/path/to/output_directory"




#Create interval
slices <- 11 #Specify number of colors in the heatmap gradient
CUTOFF <- mid <- 0.5 #Specify a cut-off
width_px <- 600 #Specify heatmap size

up <- seq(mid,1,length.out = ceiling(slices/2))
up <- up + (up[2] - up[1] )/2

down <- seq(0,mid,length.out = ceiling(slices/2))
down <- down - (down[2] - down[1] )/2

itv <- c(down,up)

#Create color table
colfn <- colorRampPalette(c("blue", "grey80","red"))
tcol <- col2rgb(colfn(slices))
colnames(tcol) <- colfn(slices)
tcol <- data.frame(t(tcol))
names(tcol) <- c("c1","c2","c3")
tcol$name <- row.names(tcol)

theme_set(theme_bw())

files <- list.files(source_dir)
files <- files[grepl(pattern = "txt",x = files)]

findat <- data.frame()

dir.create(file.path(out_dir,"Plots"))
dir.create(file.path(out_dir,"Images"))

for(file in files){
dat <- read.delim(paste0(source_dir,"/",file), header = F)
dat <- unique(dat)

for(i in 1:ncol(dat)){
  dat[,i] <- gsub(pattern = "\\[", replacement = '', dat[,i])
  dat[,i] <- gsub(pattern = "\\]", replacement = '', dat[,i])
  dat[,i] <- gsub(pattern = "'", replacement = '',dat[,i])
}

dat <- dat %>%
  separate(V2,c("true_background","true_CA","true_Benign"), sep = ' ')

dat <- dat %>%
  separate(V3,c("pred_background","pred_CA","pred_Benign"), sep = ' ')

dat$V1 <- sub(pattern = "files", replacement = "files;", dat$V1)
dat$V1 <- sub(pattern = ".jpeg", replacement = '', dat$V1)

dat <- dat %>%
  separate(V1,c("file","position"), sep = ";")
dat <- dat %>%
  separate(position,c("drop","X","Y"), sep = "_")

cols <- which(grepl(x=names(dat),pattern="true|pred|X|Y"))
for(col in cols){
  dat[,col] <- as.numeric(as.character(dat[,col]))
}

g1 <- ggplot(dat,aes(y = -Y, x =X, fill=pred_CA)) +
  geom_tile() + 
  ggtitle(paste0("Prediction:\n",file)) + 
  scale_fill_gradient2(name = "CA prob",
                       midpoint = CUTOFF,
                       high = "red",
                       low = "blue",
                       mid = "grey",
                       limit =c(0,1))+
  coord_fixed()+
  xlab("")+
  ylab("")+
  theme(axis.text = element_blank()
        ,axis.ticks = element_blank()
        ,panel.grid = element_blank()
        ,panel.border = element_blank())
g2 <- ggplot(dat,aes(y = -Y, x =X, fill=true_CA)) +
  geom_tile() + 
  ggtitle(paste0("Diagnosis:\n",file)) +
  scale_fill_gradient2(name = "CA prob",
                       midpoint = CUTOFF,
                       high = "red",
                       low = "blue",
                       mid = "grey",
                       limit =c(0,1))+
  coord_fixed()+
  xlab("")+
  ylab("")+
  theme(axis.text = element_blank()
        ,axis.ticks = element_blank()
        ,panel.grid = element_blank()
        ,panel.border = element_blank())

p <- plot_grid(g1,g2)
print(file)
ggsave(paste0(out_dir,"/Plots/",gsub(pattern = "txt",replacement = "jpg",file)),p,width =12,
       height = 6, units = "in")
findat <- rbind(findat,dat)

#Create color gradient
dat$color_pred_CA <- cut(dat$pred_CA,breaks = itv, labels = colfn(slices))
dat <- merge(dat,tcol, by.x = "color_pred_CA", by.y ="name")
dat$x <- dat$X + 1
dat$y <- dat$Y + 1
t_dat <- dat[,c("x","y","c1","c2","c3")]

mt_dat <- melt(t_dat,id.vars = c("x","y"))

mt_dat$cc <- as.numeric(sub(pattern = "c",replacement = "",as.character(mt_dat$variable)))
mt_dat$variable <- NULL
mt_dat$value <- mt_dat$value /255


canvas <- expand.grid(x = 1:max(mt_dat$x), y = 1:max(mt_dat$y),cc = 1:3)

mt_dat <- merge(canvas,mt_dat, by = c("x","y","cc"), all.x = T)
mt_dat$value[is.na(mt_dat$value)] <- 1


mt_img <- as.cimg(mt_dat) 

save.image(mt_img, paste0(out_dir,"/Images/Raw_",gsub(pattern = "txt",replacement = "jpg",file)))

big_mt_img <- resize(mt_img,width_px, width_px*height(mt_img)/width(mt_img))
save.image(big_mt_img, paste0(out_dir,"/Images//BigRaw_",gsub(pattern = "txt",replacement = "jpg",file)))



}

pred <- roc(findat$true_CA,findat$pred_CA,
            smoothed = T,
            ci = T,
            ci.alpha = 0.9,
            stratified = F,
            plot = T,
            auc.polygon = T,
            max.auc.polygon = T,
            grid = T,
            print.auc = T,
            show.thres = T)

auc(findat$true_CA,findat$pred_CA)
ci.auc(findat$true_CA,findat$pred_CA)
youden <- ci.coords(pred, x = "best", best.method = "youden")


print(youden)
