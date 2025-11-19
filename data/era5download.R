## Download Agera 5 daily data

## Install libaries
# install.packages('devtools')
library(devtools)
library(pacman)
#devtools::install_github("bluegreen-labs/ecmwfr")

# if(!require(pacman)){install.packages('pacman');library(pacman)} else {library(pacman)}
pacman::p_load(ecmwfr, lubridate, parallel)

## Add credentials ----
UID <- 'dc9d20cf-9fa8-4373-b3cf-436929c3bae4'
key <- '447bcb56-bbfe-4a91-9be7-1fc271a57fd7'

## Save key for CDS ----
ecmwfr::wf_set_key(user = UID, key = key)

## Download function for hourly data ----
getERA5_hourly <- function(i, qq, year, month, day, datadir){

    variable <- qq$variable[i]  # Acceso directo al elemento del vector
    format <- 'zip'
    ofile  <- paste0(paste(variable, year, month, day, sep = '-'), '.', format)

    if(!file.exists(file.path(datadir, ofile))){
      cat('Downloading', variable, 'for', year, month, day, '\n'); flush.console()

      # Definir todas las horas
      horas <- sprintf("%02d:00", 0:23)

      request <- list(
        dataset_short_name = 'reanalysis-era5-land',
        product_type = 'reanalysis',
        variable = variable,  # Usar la variable directamente
        year = year,
        month = month,
        day = day,
        time = horas,
        area = c(4.99, -75.61, 4.97, -75.59),  # Global
        format = format,
        target = ofile
      )

      file <- tryCatch({
        wf_request(
          request = request,
          user = UID,
          transfer = TRUE,
          path = datadir,
          verbose = FALSE
        )
      }, error = function(e){
        cat("Error en descarga:", variable, year, month, day, "-", e$message, "\n")
        return(NULL)
      })
    } else {
      cat('Ya existe', variable, 'para', year, month, day, '\n'); flush.console()
    }
    return(NULL)

  }

## Define data directory ----
datadir <- './zip_hourly'
if(!dir.exists(datadir)){dir.create(datadir, recursive = TRUE)}

## Define variables to download (ERA5-Land hourly) ----
qq <- data.frame(
  variable = c(
    '2m_temperature',
    #'2m_dewpoint_temperature',
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    #'surface_solar_radiation_downwards',
    'total_precipitation'
  )
)

## Define temporal range ----
#years <- as.character(2024)
years <- 1990:2020
months <- c(paste0('0', 1:9), 10:12)

## Do the downloads (hourly) ----
for(i in 1:nrow(qq)){
  for(year in years){
    for(month in months){
      # Calcular días del mes
      dias_mes <- days_in_month(ymd(paste(year, month, "01", sep="-")))
      dias <- sprintf("%02d", 1:dias_mes)

      for(day in dias){
        tryCatch(
          getERA5_hourly(i, qq, year, month, day, datadir),
          error = function(e){
            cat("Error en:", qq$variable[i], year, month, day, "-", e$message, "\n")
          }
        )

        # Pausa para evitar sobrecarga
        Sys.sleep(1)
      }
    }
  }
}


## Check the raster
#library(terra)
#r <- rast('D:/Datos_ERA5/Temperatures/zip_hourly/2m_temperature-2020-01-01/data.grib')
#plot(r)

## Unzipping downloads ----
#zz <- list.files(datadir, pattern = '.zip$', full.names = TRUE)

#var <- '2m_temperature'
#zz <- zz[1]
#datadir <- 'zip_hourly'


#extractNC <- function(var, zz, datadir, ncores = 1){

#z <- grep(paste0(var, '-'), zz, value = TRUE)
#fdir <- file.path(dirname(datadir), var)

#dir.create(fdir, showWarnings = FALSE, recursive = TRUE)
# lapply(z, function(x){
# unzip(x, exdir = fdir)
# fle <- list.files(fdir, full.names = T)
# fle <- grep('.grib', fle, value = T)
#rst <- rast(fle)
#out <- paste0(fdir, '/', gsub('.zip', '.tif', basename(x)))
#terra::writeRaster(x = rst, filename = out)
#file.remove(x)  # Opcional: eliminar el zip después de extraer
#file.remove(fle)
#})
#return(NULL)

#}
# Procesar cada variable
#for(var in qq$variable){
# cat("Extrayendo:", var, "\n")
# extractNC(var, zz, datadir, ncores = 1)
#}

## List the files unzipped
#dire <- './2m_temperature'
#fles <- list.files(dire, full.names = T)
#fles <- grep('.tif$', fles, value = T)
#nmes <- basename(fles)

## Read as a raster
#rstr <- terra::rast(fles)

#names(rstr)
#time(rstr)
#rstr <- rstr - 273.15
#names(rstr) <- time(rstr)

## Raster to table
#tble <- terra::as.data.frame(rstr, xy = T)
#library(tidyverse)
#tble <- tble %>% gather(var, value, -c(x, y))

#install.packages("writexl")
#library(writexl)
#write_xlsx(tble, path = "table.xlsx")
