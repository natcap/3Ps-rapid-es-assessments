library(terra)
library(raster)
library(tidyterra)
library(sf)
library(dplyr)
library(stringr)
library(exactextractr)

# This script was used to create beneficiaries maps for Armenia in the 3Ps Project

setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) # see here: https://stackoverflow.com/questions/13672720/r-command-for-setting-working-directory-to-source-file-location-in-rstudio

# Directories

  # beneficiary watersheds
  beneficiaries_folder<-"I:/Shared drives/GEF_GreenFin/Pilot_Countries/Armenia/GIS_Armenia/4_postprocess/Beneficiaries/economic_servicesheds"
  
  #Ararat RBMP area and river basins
  RBMP_area_folder<-"I:/Shared drives/GEF_GreenFin/Pilot_Countries/Armenia/GIS_Armenia/NatCap_Armenia_DataSharing/2_input_data/swy/AraratBMA_22062024/aoi_shp"
  
  
  # DEM folder 
  DEM_folder<-"I:/Shared drives/GEF_GreenFin/Pilot_Countries/Armenia/GIS_Armenia/NatCap_Armenia_DataSharing/2_input_data/swy/Hydrosheds"
  DEM_file<-"DEM_90m_Armenia_hydrosheds_raw_Rafa_prj_bilinear.tif"
  DEM<-rast(paste(DEM_folder,DEM_file,sep="/"))
  
  # water yield folder
  BF_folder<-"I:/Shared drives/GEF_GreenFin/Pilot_Countries/Armenia/GIS_Armenia/NatCap_Armenia_DataSharing/3_output_data/SWY/AraratBMA_22062024"
  BF_current_folder<-"SWY_1961_1990"
  BF_2040_folder<-"SWY_2041_2070"
  BF_2070_folder<-"SWY_2071_2100"
  
  # load data 
  BF_file<-"B_1961_1990.tif"
  BF_2040_file<-"B_2041_2070.tif"
  BF_2070_file<-"B_2071_2100.tif"
  
  BF<-rast(paste(BF_folder,BF_current_folder,BF_file,sep="/"))
  BF_2040<-rast(paste(BF_folder,BF_2040_folder,BF_2040_file,sep="/"))
  BF_2070<-rast(paste(BF_folder,BF_2070_folder,BF_2070_file,sep="/"))
  
  BF<-resample(BF,DEM,method="bilinear")
  BF_2040<-resample(BF_2040,DEM,method="bilinear")
  BF_2070<-resample(BF_2070,DEM,method="bilinear")
  
  AraratRBMP<-read_sf(paste(RBMP_area_folder,"aoi.shp",sep="/")) %>% filter(RB_NameEng==c("Azat","Vedi","Arpa") )
  

  #output folder
  Out_folder<-"I:/Shared drives/GEF_GreenFin/Pilot_Countries/Armenia/GIS_Armenia/NatCap_Armenia_DataSharing/4_postprocess/valuation"
  
#### Analysis
  
  # load servicesheds, match attributes and join servicesheds for fish, irrigation, hydropower together.
  
  # load shapefiles
    bf_ws_ff<-read_sf(paste(beneficiaries_folder,"ff_beneficiearies_servicesheds.shp",sep="/"))
    bf_ws_shp<-read_sf(paste(beneficiaries_folder,"shpp_beneficiaries_servicesheds.shp",sep='/'))
    bf_ws_irri<-read_sf(paste(beneficiaries_folder,"irrigation_beneficiaries_servicesheds.shp",sep="/"))
    
  # assign type
    bf_ws_ff$type="Fish Farm"
    bf_ws_shp$type="Hydropower"
    bf_ws_irri$type="Agriculture"
    

  # keep only few, identical fields for each type of beneficiary  
    bf_ws_ff=bf_ws_ff %>% select("type","Rev_AMD")
    bf_ws_shp=bf_ws_shp %>% select("type","Rev_AMD")
    bf_ws_irri=bf_ws_irri %>% select("type","Rev_AMD")
    
  # combine all beneficiary shapefiles in 1
    bf_ws_comb<-rbind(bf_ws_ff,bf_ws_shp,bf_ws_irri)
    
    # calculate value per m2. Note: remove units, because if the attribute used for accumulation has units attached, then the summation below will NOT work.
    bf_ws_ff$area_m2<-st_area(bf_ws_ff) %>% as.vector()
    bf_ws_shp$area_m2<-st_area(bf_ws_shp) %>% as.vector()
    bf_ws_irri$area_m2<-st_area(bf_ws_irri) %>% as.vector()
    
         
    bf_ws_ff$value_per_m2<-bf_ws_ff$Rev_AMD/bf_ws_ff$area_m2
    bf_ws_shp$value_per_m2<-bf_ws_shp$Rev_AMD/bf_ws_shp$area_m2
    bf_ws_irri$value_per_m2<-bf_ws_irri$Rev_AMD/bf_ws_irri$area_m2
    
  ### rasterized approach

    # make storage structs
    bf_ws_ff_stack<-list() #  for fishfarms
    bf_ws_shp_stack<-list() #  for hydropower
    bf_ws_irri_stack<-list() # for irrigation
    
    # loop through beneficiary types
          # loop through fishfarms
          for (ii in 1:nrow(bf_ws_ff)){
            
            bf_ws_ff_stack[[ii]]<-rasterize(x=bf_ws_ff[ii,],
                                          y=DEM,
                                          field="value_per_m2")
          }
          
          # loop through shp
          for (ii in 1:nrow(bf_ws_shp)){
            
            bf_ws_shp_stack[[ii]]<-rasterize(x=bf_ws_shp[ii,],
                                                y=DEM,
                                                field="value_per_m2")
          }
          
          # loop through irrigation
          for (ii in 1:nrow(bf_ws_irri)){
            
            bf_ws_irri_stack[[ii]]<-rasterize(x=bf_ws_irri[ii,],
                                             y=DEM,
                                             field="value_per_m2")
          }
    
    # get total values for each beneficiary type
    bf_ws_ff_r<-app(rast(bf_ws_ff_stack),fun=sum,na.rm=T) %>% rename("fish farms"=sum)#  for fish farms
    bf_ws_shp_r<-app(rast(bf_ws_shp_stack),fun=sum,na.rm=T) %>% rename("hydropower"=sum) #  for hydropower
    bf_ws_irri_r<-app(rast(bf_ws_irri_stack),fun=sum,na.rm=T) %>% rename("irrigation"=sum)# for irrigation
    
    # combine total sectoral values into raster stack
    r<-c(bf_ws_ff_r,
      bf_ws_irri_r,
      bf_ws_shp_r)

    plot(r)
    
    # total value
    bf_ws_tot_r  <- app(c(bf_ws_ff_r,
                          bf_ws_irri_r,
                          bf_ws_shp_r),
                        fun=sum,na.rm=T) %>% rename("total value"=sum)
                              
    
    
    
    plot(bf_ws_tot_r)
    
  # write outputs rasters of cummulative water yield  
    
    writeRaster(bf_ws_tot_r,paste(Out_folder,
                                  "Total_cum_water_value_v2.tif",
                                  sep="/"),
                overwrite=T)
    
    writeRaster(bf_ws_ff_r,paste(Out_folder,
                                  "FF_cum_water_value_v2.tif",
                                  sep="/"),
                overwrite=T)
    
    writeRaster(bf_ws_shp_r,paste(Out_folder,
                                  "SHP_cum_water_value_v2.tif",
                                  sep="/"),
                overwrite=T)
    
    writeRaster(bf_ws_irri_r,paste(Out_folder,
                                  "IRRI_cum_water_value_v2.tif",
                                  sep="/"),
                overwrite=T)
    
    ### testing
    plot(BF)
    
    ind1<-bf_ws_tot_r*BF
    names(ind1)<-  "current"
    ind1_2070=bf_ws_tot_r*BF_2070 
    names(ind1_2070)<-  "2070"
    ind1_2040=bf_ws_tot_r*BF_2040 
    names(ind1_2040)<-  "2040"
    
    plot(c(ind1))
    plot((ind1_2070-ind1))
    plot((ind1_2040-ind1))
    
    writeRaster(ind1,paste(Out_folder,
                                  "Water_value_indicator_v2.tif",
                                  sep="/"),
                overwrite=T)
    
    writeRaster(ind1_2070-ind1,paste(Out_folder,
                           "Change_Water_value_indicator_2070min1990_v2.tif",
                           sep="/"),
                overwrite=T)
    
    
    writeRaster(ind1_2040-ind1,paste(Out_folder,
                                     "Change_Water_value_indicator_2040min1990_v2.tif",
                                     sep="/"),
                overwrite=T)
    
    # decrease in baseflow 
        # for the whole area
        perc_dec_bf_2040<-(BF_2040-BF)/BF*100
        perc_dec_bf_2070<-(BF_2070-BF)/BF*100
    
        global(perc_dec_bf_2040,mean,na.rm=T)
        global(perc_dec_bf_2040,min,na.rm=T)
        global(perc_dec_bf_2040,max,na.rm=T)
    
        global(perc_dec_bf_2070,mean,na.rm=T)
        global(perc_dec_bf_2070,min,na.rm=T)
        global(perc_dec_bf_2070,max,na.rm=T)
        
        # per basin 
        BF_reduction_per_basin<-data.frame("2040_2070"=exact_extract(perc_dec_bf_2040,AraratRBMP,"mean"),
                                           "2071_2100"=exact_extract(perc_dec_bf_2070,AraratRBMP,"mean"), 
                                           row.names=AraratRBMP$RB_NameEng)
        
        # global 
        BF_reduction_global<-data.frame("2040_2070"=c(
          exact_extract(perc_dec_bf_2040 ,AraratRBMP%>% st_union(),"mean"), 
          exact_extract(perc_dec_bf_2040,AraratRBMP %>% st_union(),"min"),  
          exact_extract(perc_dec_bf_2040 ,AraratRBMP%>% st_union(),"max")),
          "2071_2100"=c(
            exact_extract(perc_dec_bf_2070,AraratRBMP %>% st_union(),"mean"), 
            exact_extract(perc_dec_bf_2070 ,AraratRBMP %>% st_union(),"min"),  
            exact_extract(perc_dec_bf_2070 ,AraratRBMP%>% st_union(),"max")), 
          row.names=c("MEAN","MIN","MAX"))
        
        
        
    