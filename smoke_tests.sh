#!/usr/bin/env bash
. /opt/smoke.sh/smoke.sh

hostname=$(hostname)
smoke_url_ok "http://${hostname}/api/recommend-reviewers?manuscript_no=xyz&subject_area=&keywords=&abstract="
smoke_url_ok "http://${hostname}/api/recommend-reviewers?manuscript_no=18449&subject_area=&keywords=&abstract="

smoke_report
