#' Download spatial data of meso regions
#'
#' @description
#' Data at scale 1:250,000, using Geodetic reference system "SIRGAS2000" and CRS(4674)
#'
#' @template year
#' @param code_meso The 4-digit code of a meso region. If the two-digit code or
#'        a two-letter uppercase abbreviation of a state is passed, (e.g. 33 or
#'        "RJ") the function will load all meso regions of that state. If
#'        `code_meso="all"` (Default), the function downloads all meso
#'        regions of the country.
#' @template simplified
#' @template showProgress
#' @template cache
#'
#' @return An `"sf" "data.frame"` object
#'
#' @export
#' @family area functions
#'
#' @examplesIf identical(tolower(Sys.getenv("NOT_CRAN")), "true")
#' # Read specific meso region at a given year
#'   meso <- read_meso_region(code_meso=3301, year=2018)
#'
#' # Read all meso regions of a state at a given year
#'   meso <- read_meso_region(code_meso=12, year=2017)
#'   meso <- read_meso_region(code_meso="AM", year=2000)
#'
#' # Read all meso regions of the country at a given year
#'   meso <- read_meso_region(code_meso="all", year=2010)
#'
read_meso_region <- function(year = NULL,
                             code_meso = "all",
                             simplified = TRUE,
                             showProgress = TRUE,
                             cache = TRUE){

  # Get metadata with data url addresses
  temp_meta <- select_metadata(geography="meso_region",
                               year=year,
                               simplified=simplified)

  # check if download failed
  if (is.null(temp_meta)) { return(invisible(NULL)) }

  # Verify code_meso input
  if (!any(code_meso == 'all' |
           code_meso %in% temp_meta$code |
           substring(code_meso, 1, 2) %in% temp_meta$code |
           code_meso %in% temp_meta$code_abbrev
  )) {
    stop("Error: Invalid Value to argument code_meso.")
  }

  # get file url
  if (code_meso=="all") {
    file_url <- as.character(temp_meta$download_path)

  } else if (is.numeric(code_meso)) { # if using numeric code_meso
    file_url <- as.character(subset(temp_meta, code==substr(code_meso, 1, 2))$download_path)

  } else if (is.character(code_meso)) { # if using chacracter code_abbrev
    file_url <- as.character(subset(temp_meta, code_abbrev==substr(code_meso, 1, 2))$download_path)
  }

  # download gpkg
  temp_sf <- download_gpkg(file_url = file_url,
                           showProgress = showProgress,
                           cache = cache)

  # check if download failed
  if (is.null(temp_sf)) { return(invisible(NULL)) }

  ## FILTERS
  y <- code_meso

  # input "all"
  if (code_meso=="all" | nchar(code_meso)==2) {

  #   # abbrev_state
  # } else if (code_meso %in% temp_sf$abbrev_state){
  #   temp_sf <- subset(temp_sf, abbrev_state == y)
  #
  #   # code_state
  # } else if (code_meso %in% substring(temp_sf$code_meso,1,2)) {
  #   temp_sf <- subset(temp_sf, substring(code_meso,1,2) == y)

    # code_meso
  } else if (code_meso %in% temp_sf$code_meso) {
    temp_sf <- subset(temp_sf, code_meso == y)

  } else {stop(paste0("Error: Invalid Value to argument 'code_meso'",collapse = " "))}

  return(temp_sf)
}
