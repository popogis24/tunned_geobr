% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/read_health_region.R
\name{read_health_region}
\alias{read_health_region}
\title{Download spatial data of Brazilian health regions and health macro regions}
\usage{
read_health_region(
  year = NULL,
  macro = FALSE,
  simplified = TRUE,
  showProgress = TRUE,
  cache = TRUE
)
}
\arguments{
\item{year}{Numeric. Year of the data in YYYY format. It defaults to \code{NULL}
and reads the data from the latest year available.}

\item{macro}{Logic. If \code{FALSE} (default), the function downloads health
regions data. If \code{TRUE}, the function downloads macro regions data.}

\item{simplified}{Logic \code{FALSE} or \code{TRUE}, indicating whether the function
should return the data set with 'original' spatial resolution or a data set
with 'simplified' geometry. Defaults to \code{TRUE}. For spatial analysis and
statistics users should set \code{simplified = FALSE}. Borders have been
simplified by removing vertices of borders using \verb{st_simplify\{sf\}} preserving
topology with a \code{dTolerance} of 100.}

\item{showProgress}{Logical. Defaults to \code{TRUE} display progress bar.}

\item{cache}{Logical. Whether the function should read the data cached
locally, which is faster. Defaults to \code{cache = TRUE}. By default,
\code{geobr} stores data files in a temporary directory that exists only
within each R session. If \code{cache = FALSE}, the function will download
the data again and overwrite the local file.}
}
\value{
An \verb{"sf" "data.frame"} object
}
\description{
Health regions are used to guide the the regional and state planning of health services.
Macro health regions, in particular, are used to guide the planning of high complexity
health services. These services involve larger economics of scale and are concentrated in
few municipalities because they are generally more technology intensive, costly and face
shortages of specialized professionals. A macro region comprises one or more health regions.
}
\examples{
\dontshow{if (identical(tolower(Sys.getenv("NOT_CRAN")), "true")) (if (getRversion() >= "3.4") withAutoprint else force)(\{ # examplesIf}
# Read all health regions for a given year
hr <- read_health_region( year=2013 )

# Read all macro health regions
mhr <- read_health_region( year=2013, macro =TRUE)
\dontshow{\}) # examplesIf}
}
\seealso{
Other area functions: 
\code{\link{read_amazon}()},
\code{\link{read_biomes}()},
\code{\link{read_capitals}()},
\code{\link{read_comparable_areas}()},
\code{\link{read_country}()},
\code{\link{read_disaster_risk_area}()},
\code{\link{read_health_facilities}()},
\code{\link{read_immediate_region}()},
\code{\link{read_indigenous_land}()},
\code{\link{read_intermediate_region}()},
\code{\link{read_meso_region}()},
\code{\link{read_metro_area}()},
\code{\link{read_micro_region}()},
\code{\link{read_municipal_seat}()},
\code{\link{read_municipality}()},
\code{\link{read_neighborhood}()},
\code{\link{read_pop_arrangements}()},
\code{\link{read_region}()},
\code{\link{read_schools}()},
\code{\link{read_semiarid}()},
\code{\link{read_state}()},
\code{\link{read_statistical_grid}()},
\code{\link{read_urban_area}()},
\code{\link{read_urban_concentrations}()},
\code{\link{read_weighting_area}()}
}
\concept{area functions}
