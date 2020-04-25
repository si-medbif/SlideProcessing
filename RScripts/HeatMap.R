suppressPackageStartupMessages(library(imager))
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(reshape2))
suppressPackageStartupMessages(library(argparser))
suppressPackageStartupMessages(library(Xmisc))
suppressPackageStartupMessages(library(fs))

#Load argparser
p <- arg_parser("Converting a prediction file to a heatmap and a resized (zoomed) heatmap")
p <- add_argument(p,"--input", type="character",
                  help="Path to a prediction file (txt file).")
p <- add_argument(p,"--vips", type="character",
                  help="Path to a directory containing tile files processed by VIPS.")
p <- add_argument(p, "--out_dir", type="character",
                  help="Path to an output directory." )
p <- add_argument(p, "--mag", type="numeric",default=10,
                  help="Magnification level of the tile files. Posible values are 5, 10, 20 and 40" )
p <- add_argument(p, "--cut_off", type="numeric",default=0.5,
                  help="Cut-off for classification")
p <- add_argument(p, "--slices", type="numeric",default=10,
                  help="Number of colors for a gradient scale for the heatmap")
p <- add_argument(p, "--width", type="numeric",default=1000,
                  help="Width in pixels of a resized heatmap using in the web application")

args <- parse_args(p)


#Specify Variable here
input <- args$input #"~/DeepLearning/FlowTest/Slides_Prediction/SX17003727_A10-1_HE_files.txt"
slide_name <- path_split(input)[[1]]
slide_name <- slide_name[length(slide_name)]
mag_level <- args$mag #10
VIPS_path <- args$vips #"~/DeepLearning/FlowTest/Slides_Dzi/SX17003727_A10-1_HE_files/"
slices <- 1 + args$slices #11
CUTOFF <- mid <- args$cut_off #0.5
width_px <- args$width #1000

#Load input file
dat <- read.delim(input, header = F)
dat <- unique(dat)

#Extract maxX maxY from VIPS
mag_df <- data.frame(mag = c(5,10,20,40), mag_index = c(4,3,2,1)) 
mag_index <- mag_df$mag_index[mag_df$mag == mag_level]
VIPS_dirs <- as.numeric(as.character(list.files(VIPS_path)))
VIPS_dirs <- VIPS_dirs[order( -VIPS_dirs )]
VIPS_dir <-  VIPS_dirs[mag_index]

VIPS_files <- data.frame(fname = gsub("\\.jpeg","",list.files(file.path(VIPS_path,VIPS_dir))))
VIPS_files <- VIPS_files %>%
  separate(fname, c("x","y"),sep = "_")

MaxX <- max(as.numeric(as.character(VIPS_files$x)),na.rm = T)
MaxY <- max(as.numeric(as.character(VIPS_files$y)),na.rm = T)

#Prepare data
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

#Create interval
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


canvas <- expand.grid(x = 1:(MaxX+1), y = 1:(MaxY+1),cc = 1:3)

mt_dat <- merge(canvas,mt_dat, by = c("x","y","cc"), all.x = T)
mt_dat$value[is.na(mt_dat$value)] <- 1


mt_img <- as.cimg(mt_dat) 

save.image(mt_img, paste0(rstrip(args$out_dir,"/"),"/Original/",rstrip(slide_name,"txt"),"jpeg"))

big_mt_img <- resize(mt_img,width_px, width_px*height(mt_img)/width(mt_img))

save.image(big_mt_img, paste0(rstrip(args$out_dir,"/"),"/Resized/Resized_",rstrip(slide_name,"txt"),"jpeg"))


