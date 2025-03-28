############# Support functions for geobr
# nocov start



#' Select data type: 'original' or 'simplified' (default)
#'
#'
#' @param temp_meta A dataframe with the file_url addresses of geobr datasets
#' @param simplified Logical TRUE or FALSE indicating  whether the function returns the 'original' dataset with high resolution or a dataset with 'simplified' borders (Defaults to TRUE)
#' @keywords internal
#'
select_data_type <- function(temp_meta, simplified=NULL){

  if (!is.logical(simplified)) { stop(paste0("Argument 'simplified' needs to be either TRUE or FALSE")) }

  if(isTRUE(simplified)){
    temp_meta <- temp_meta[  grepl(pattern="simplified", temp_meta$download_path), ]
  }

  if(isFALSE(simplified)){
    temp_meta <- temp_meta[  !(grepl(pattern="simplified", temp_meta$download_path)), ]
  }

  return(temp_meta)
}





#' Select year input
#'
#' @param temp_meta A dataframe with the file_url addresses of geobr datasets
#' @param y Year of the dataset (passed by red_ function)
#' @keywords internal
#'
select_year_input <- function(temp_meta, y=year){

  # NULL = use latest year available
  if (is.null(y)){
    y <- max(temp_meta$year)
  }

  # invalid input
  if (y %in% temp_meta$year) {
    message(paste0("Using year/date ", y))
    temp_meta <- subset(temp_meta, year == y)
    return(temp_meta)
    }

  # invalid input
  else { stop(paste0("Error: Invalid Value to argument 'year/date'. It must be one of the following: ",
                         paste(unique(temp_meta$year), collapse = " ")))
    }
}


#' Select metadata
#'
#' @param geography Which geography will be downloaded.
#' @param simplified Logical TRUE or FALSE indicating  whether the function
#'        returns the 'original' dataset with high resolution or a dataset with
#'        'simplified' borders (Defaults to TRUE).
#' @param year Year of the dataset (passed by read_ function).
#'
#' @keywords internal
#' @examples \dontrun{ if (interactive()) {
#'
#' library(geobr)
#'
#' df <- download_metadata()
#'
#' }}
#'
select_metadata <- function(geography, year=NULL, simplified=NULL){

# download metadata
  metadata <- download_metadata()

  # check if download failed
  if (is.null(metadata)) { return(invisible(NULL)) }

  # Select geo
  temp_meta <- subset(metadata, geo == geography)

  # Select year input
  temp_meta <- select_year_input(temp_meta, y=year)

  # Select data type
  temp_meta <- select_data_type(temp_meta, simplified=simplified)

  return(temp_meta)
}


#' Support function to download metadata internally used in geobr
#'
#'
#' @keywords internal
#' @examples \dontrun{ if (interactive()) {
#' df <- download_metadata()
#' }}
download_metadata <- function(){ # nocov start

  # create tempfile to save metadata
  tempf <- fs::path(fs::path_temp(), "metadata_geobr_gpkg.csv")

  # IF metadata has already been successfully downloaded
  if (file.exists(tempf) & file.info(tempf)$size != 0) {

  } else {

  # test server connection with github
  metadata_link <- 'https://github.com/ipeaGIT/geobr/releases/download/v1.7.0/metadata_1.7.0_gpkg.csv'
  try( silent = TRUE,
       check_con <- check_connection(metadata_link, silent = TRUE)
  )

  # if connection with github fails, try connection with ipea
  if (is.null(check_con) | isFALSE(check_con)) {
    metadata_link <- 'https://www.ipea.gov.br/geobr/metadata/metadata_1.7.0_gpkg.csv'
    try( silent = TRUE,
         check_con <- check_connection(metadata_link, silent = FALSE)
    )

    if (is.null(check_con) | isFALSE(check_con)) { return(invisible(NULL)) }
  }

  # download metadata to temp file
  try( silent = TRUE,
       downloaded_files <- curl::multi_download(
         urls = metadata_link,
         destfiles = tempf,
         resume = TRUE,
         progress = FALSE
       )
  )

  # if anything fails, return NULL
  if (any(!downloaded_files$success | is.na(downloaded_files$success))) {
    msg <- paste("File cached locally seems to be corrupted. Please download it again.")
    message(msg)
    return(invisible(NULL))
  }
  }

  # read metadata
  # metadata <- data.table::fread(tempf, stringsAsFactors=FALSE)
  metadata <- utils::read.csv(tempf, stringsAsFactors=FALSE)

  # check if data was read Ok
  if (nrow(metadata)==0) {
    message("A file must have been corrupted during download. Please restart your R session and download the data again.")
    return(invisible(NULL))
  }

  return(metadata)
} # nocov end



#' Download geopackage to tempdir
#'
#' @param file_url A string with the file_url address of a geobr dataset
#' @template showProgress
#' @template cache
#' @keywords internal
#'
download_gpkg <- function(file_url = parent.frame()$file_url,
                          showProgress = parent.frame()$showProgress,
                          cache = parent.frame()$cache){

  if (!is.logical(showProgress)) { stop("'showProgress' must be of type 'logical'") }
  if (!is.logical(cache)) { stop("'cache' must be of type 'logical'") }

  # get backup links
  filenames <- basename(file_url)
  file_url2 <- paste0('https://github.com/ipeaGIT/geobr/releases/download/v1.7.0/', filenames)

  # dest files
  # temps <- paste0(fs::path_temp(),"/", unlist(lapply(strsplit(file_url,"/"),tail,n=1L)))
  temps <- fs::path(fs::path_temp(), basename(file_url))

  # test connection with server1
    try( silent = TRUE, check_con <- check_connection(file_url[1], silent = TRUE))

    # if server1 fails, replace url and test connection with server2
    if (is.null(check_con) | isFALSE(check_con)) {
      file_url <- file_url2
      try( silent = TRUE, check_con <- check_connection(file_url[1], silent = FALSE))
      if (is.null(check_con) | isFALSE(check_con)) { return(invisible(NULL)) }
    }

  # # this is necessary to silence download message when reading local file
  # if(file.exists(temps) & isTRUE(cache)){
  #   showProgress <- FALSE
  # }

  # download files
  try(silent = TRUE,
      downloaded_files <- curl::multi_download(
        urls = file_url,
        destfiles = temps,
        progress = showProgress,
        resume = cache
        )
      )

  # if anything fails, return NULL
  if (any(!downloaded_files$success | is.na(downloaded_files$success))) {
    msg <- paste("File cached locally seems to be corrupted. Please download it again.")
    message(msg)
    return(invisible(NULL))
  }

  # load gpkg
  temp_sf <- load_gpkg(temps) #
  return(temp_sf)
}







#' Load geopackage from tempdir to global environment
#'
#' @param temps The address of a gpkg file stored in tempdir. Defaults to NULL
#' @keywords internal
#'
load_gpkg <- function(temps=NULL){

  ### one single file

  if (length(temps)==1) {

    # read sf
    temp_sf <- sf::st_read(temps, quiet=TRUE)
  }

  else if(length(temps) > 1){

    # read files and pile them up
    files <- lapply(X=temps, FUN= sf::st_read, quiet=TRUE)
    # temp_sf <- sf::st_as_sf(data.table::rbindlist(files, fill = TRUE)) # do.call('rbind', files)
    temp_sf <- dplyr::bind_rows(files)

    # closes issue 284
    col1 <- names(temp_sf)[1]
    temp_sf <- subset(temp_sf, get(col1) != 'data_table_sf_bug')

    # remove data.table from object class. Closes #279.
    class(temp_sf) <- c("sf", "data.frame")

  }

  # check if data was read Ok
  if (nrow(temp_sf)==0) {
    message("A file must have been corrupted during download. Please restart your R session and download the data again.")
    return(invisible(NULL))
  }
  return(temp_sf)

  # load gpkg to memory
  temp_sf <- load_gpkg(temps)
  return(temp_sf)
}


# nocov end



#' Check internet connection with Ipea server
#'
#' @description
#' Checks if there is an internet connection with Ipea server.
#'
#' @param url A string with the url address of an aop dataset
#' @param silent Logical. Throw a message when silent is `FALSE` (default)
#'
#' @return Logical. `TRUE` if url is working, `FALSE` if not.
#'
#' @keywords internal
#'
check_connection <- function(url = 'https://www.ipea.gov.br/geobr/metadata/metadata_gpkg.csv',
                             silent = FALSE){ # nocov start
  # url <- 'https://google.com/'               # ok
  # url <- 'https://www.google.com:81/'   # timeout
  # url <- 'https://httpbin.org/status/300' # error

  # Check if user has internet connection
  if (!curl::has_internet()) {
    if (isFALSE(silent)) {
      message("No internet connection.")
    }
    return(FALSE)
  }

  # Message for connection issues
  msg <- "Problem connecting to data server. Please try again in a few minutes."

  # Test server connection using curl
  handle <- curl::new_handle(ssl_verifypeer = FALSE)
  response <- try(curl::curl_fetch_memory(url, handle = handle), silent = TRUE)

  # Check if there was an error during the fetch attempt
  if (inherits(response, "try-error")) {
    if (isFALSE(silent)) {
      message(msg)
    }
    return(FALSE)
  }

  # Check the status code
  status_code <- response$status_code

  # Link working fine
  if (status_code == 200L) {
    return(TRUE)
  }

  # Link not working or timeout
  if (status_code != 200L) {
    if (isFALSE(silent)) {
      message(msg)
    }
    return(FALSE)
  }
} # nocov end



#' Check if vector only has numeric characters
#'
#' @description
#' Checks if vector only has numeric characters
#'
#' @param x A vector.
#'
#' @return Logical. `TRUE` if vector only has numeric characters.
#'
#' @keywords internal
numbers_only <- function(x){ !grepl("\\D", x) } # nocov



#' Filter data set to return specific states
#'
#' @param temp_sf An internal simple feature or data.frame
#' @param code The two-digit code of a state or a two-letter uppercase
#'             abbreviation (e.g. 33 or "RJ"). If `code_state="all"` (the
#'             default), the function downloads all states.
#'
#' @return A simple feature `sf` or `data.frame`.
#'
#' @keywords internal
filter_state <- function(temp_sf = parent.frame()$temp_sf,
                         code = parent.frame()$code_state
                         ){ # nocov start

  error_message1 <- "This 'code_state' does not exist or it is not present in this data set."
  error_message2 <- "The 'code_state' comprise only numbers OR letters. It does not accept mixing numbers and letters."

  # all states
  if (any(code == 'all')) {return(temp_sf)}

  # only numbers with code states
  if (all(numbers_only(code))) {

    if (!all(code %in% unique(temp_sf$code_state))) {stop(error_message1)}

    temp <- subset(temp_sf, code_state %in% code)
    return(temp)
  }

  # only letters with state abbreviation
  if (all(!numbers_only(code))) {

    if (!all(code %in% unique(temp_sf$abbrev_state))) {stop(error_message1)}

    temp <- subset(temp_sf, abbrev_state %in% code)
    return(temp)
  }

  stop(error_message2)

} # nocov end
