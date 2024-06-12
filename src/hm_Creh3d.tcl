namespace eval ::hmCreH3d {
	# Effectiveness of analysis(True:1 or False:0)
	variable analysisValidity;
	# Array of thickness-dict[key=nodeID, value=thickness] ("omote", "hojyo", "rimen", "omotehojyo", "omoterimen", "omotehojyorimen") 
	variable thicknessValues;
	# Array of density-dict[key=nodeID, value=density] ("omote", "hojyo", "rimen", "omotehojyo", "omoterimen", "omotehojyorimen") 
	variable densityValues;
	# Array of Element list for H3D ("omote", "hojyo", "rimen". In other case, "omote" is used.)
	variable relatedElements;
	# Array of Node list for H3D ("omote", "hojyo", "rimen". In other case, "omote" is used.)
	variable relatedNodes;
	# Film thickness specification value
	variable specificationThickness;
	# Rimen structure evalustion flag(True:1 or False:0)
	variable rimenStructureEvaluation;
}

proc ::hmCreH3d::main {args} {
	::hmCreH3d::explog 0 "##### HM script #####";

 	if {[catch {::hmCreH3d::Initialize} code option]} {
		::hmCreH3d::explog 1 "Error Initialize: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::ReadAnalysisValidity} code option]} {
		::hmCreH3d::explog 1 "Error ReadAnalysisValidity: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::ReadModel} code option]} {
		::hmCreH3d::explog 1 "Error ReadModel: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::ReadResult} code option]} {
		::hmCreH3d::explog 1 "Error ReadResult: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::OutputText} code option]} {
		::hmCreH3d::explog 1 "Error OutputText: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::OutputH3D} code option]} {
		::hmCreH3d::explog 1 "Error OutputH3D: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::OutputMaxMin} code option]} {
		::hmCreH3d::explog 1 "Error OutputMaxMin: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::OutputNG} code option]} {
		::hmCreH3d::explog 1 "Error OutputNG: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	if {[catch {::hmCreH3d::OutputMaxOnRimen} code option]} {
		::hmCreH3d::explog 1 "Error OutputMaxOnRimen: $code $option" 1;
		::hmCreH3d::errfile;
		return 1;
	}

	::hmCreH3d::explog 1 "End HM script.";
	return 0;
}

proc ::hmCreH3d::explog {{flg 0} {msgD ""} {err 0} args} {
	if { $msgD == "" } {
		return 1;
	}

	set logpath "./CreRepMsg.log";
	set type [expr {$flg == 1 ? "a" : "w"}];
	set logType [expr {$err == 1 ? "\[ERROR\]" : "\[INFO\]"}];
	set timeStmp [clock format [clock seconds] -format {%m/%d %H:%M:%S}]

	set chid [open "${logpath}" $type];
	puts $chid "$timeStmp $logType $msgD"
	close $chid;

	return 0;
}

#####
proc ::hmCreH3d::errfile {args} {
	set fileN  "./Errorflg"
	set chid [open "${fileN}" w];
	close $chid;
	return 0;
}

proc ::hmCreH3d::Initialize {args} {
	hm_commandfilestate 1;

	# output directory
	if {[file isdirectory ./temp] == 1} {
		catch {file delete -force ./temp} res;
	}
	catch {file mkdir ./temp} res;

	# delete old error file
	if {[file isfile ./Errorflg] == 1} {
		catch {file delete -force ./Errorflg} res;
	}

	return 0
}

proc ::hmCreH3d::ReadAnalysisValidity {args} {
	variable analysisValidity;
	variable specificationThickness;
	variable thresholdLowerLimit
	variable thresholdUpperLimitDS;
	variable thresholdUpperLimitPL;
	variable rimenStructureEvaluation;
	variable thicknessEvaluationPitch;

	array set analysisValidity {"omote" 0 "hojyo" 0 "rimen" 0 "omotehojyo" 0 "omoterimen" 0 "omotehojyorimen" 0}
	set specificationThickness 50.0;
	set thresholdLowerLimit 25;
	set thresholdUpperLimitDS 90;
	set thresholdUpperLimitPL 70;
	set rimenStructureEvaluation 0;
	set thicknessEvaluationPitch 100;

	set spath "./analysis_conditions.txt";
	if {[file exists $spath] == 0 } {
		::hmCreH3d::explog 1 "Analysis condition file was not found." 1;
		error 1;
	}

	set chid [open "${spath}" r];
	while {! [eof $chid]} {
		# Read one line, trim with blanks and "
		set line [string trim [gets $chid]];
		set lines [split $line ":"];
		if {[llength $lines] < 2} {
			continue;
		}

		# Get key and value (key = "A020", value = 1)
		set key [ lindex $lines 0 ];
		set value [ lindex $lines 1 ];

		if { $key == "A020" } {
			# 主陽極解析タイプ_1-5
			if { ![ string is integer -strict $value ] } {
				continue;
			}
			if { 1 <= $value && $value <= 5 } {
				set analysisValidity(omote) 1;
			}
		}
		if { $key == "A022" } {
			# 補助極解析タイプ_6-8
			if { ![ string is integer -strict $value ] } {
				continue;
			}
			# if $value == 8, analysisValidity(hojyo) = 0;
			if { 6 <= $value && $value <= 7 } {
				set analysisValidity(hojyo) 1;
			}
		}
		if { $key == "A024" } {
			# 裏面陽極解析タイプ_9-10
			if { ![ string is integer -strict $value ] } {
				continue;
			}
			# if $value == 10, analysisValidity(rimen) = 0;;
			if { $value == 9 } {
				set analysisValidity(rimen) 1;
			}
		}
		if { $key == "A017" } {
			# 膜厚指定値
			if { ![ string is double -strict $value ] } {
				continue;
			}
			set specificationThickness $value;
		}
		if { $key == "A026" } {
			# 閾値判定基準_膜厚下限値
			if { ![ string is double -strict $value ] } {
				continue;
			}
			set thresholdLowerLimit $value;
		}
		if { $key == "A027" } {
			# 閾値判定基準_膜厚上限値(意匠面)
			if { ![ string is double -strict $value ] } {
				continue;
			}
			set thresholdUpperLimitDS $value;
		}
		if { $key == "A028" } {
			# 閾値判定基準_膜厚上限値(PL)
			if { ![ string is double -strict $value ] } {
				continue;
			}
			set thresholdUpperLimitPL $value;
		}
		if { $key == "A066" } {
			# 裏面構造物評価の有無
			if { ![ string is boolean -strict $value ] } {
				continue;
			}
			set rimenStructureEvaluation 1;
		}
		if { $key == "A083" } {
			# 膜厚評価ピッチ
			if { ![ string is double -strict $value ] } {
				continue;
			}
			if { $value > 0.0 } {
				set thicknessEvaluationPitch $value;
			}
		}
	}

	# 主陽極解析 + 補助極解析
	if { $analysisValidity(omote) && $analysisValidity(hojyo) } {
		set analysisValidity(omotehojyo) 1
	}
	# 主陽極解析 + 裏面陽極解析
	if { $analysisValidity(omote) && $analysisValidity(rimen) } {
		set analysisValidity(omoterimen) 1
	}
	# 主陽極解析 + 補助極解析 + 裏面陽極解析
	if { $analysisValidity(omote) && $analysisValidity(hojyo) && $analysisValidity(rimen) } {
		set analysisValidity(omotehojyorimen) 1
	}

	::hmCreH3d::explog 1 "Analysis validity: omote=$analysisValidity(omote), hojyo=$analysisValidity(hojyo), rimen=$analysisValidity(rimen),\
		omote&hojyo=$analysisValidity(omotehojyo), omote&rimen=$analysisValidity(omoterimen), omote&hojyo&rimen=$analysisValidity(omotehojyorimen)";
	::hmCreH3d::explog 1 "Thickness threshold: specificationThickness=$specificationThickness,\
		thresholdLowerLimit=$thresholdLowerLimit, thresholdUpperLimitDS=$thresholdUpperLimitDS, thresholdUpperLimitPL=$thresholdUpperLimitPL";
	::hmCreH3d::explog 1 "Report parameter: thicknessEvaluationPitch=$thicknessEvaluationPitch";
	close $chid;

	return 0;
}

proc ::hmCreH3d::ReadModel {args} {
	set modelpath "./PreModel.fem"

	if {[file exists "$modelpath"] == 0 || [file size "$modelpath"] == 0} {
		::hmCreH3d::explog 1 "FEM file was not found. Modeling has failed. <$modelpath>" 1;
		error 1;
	}

	*displayimporterrors 0;
	*feinputwithdata2 "#optistruct/optistruct" "$modelpath" 0 0 0 0 0 1 8 1 0;

	# 削除
	eval *createmark comps 1 "by name" Tub Anode;
	set numOfComps [ hm_marklength comps 1 ];
	if { $numOfComps > 0 } {
		*deletemark comps 1;
		::hmCreH3d::explog 1 "Deleted component. Number of comps = $numOfComps";
	}

	# 必要な箇所だけ残したFEMを出力
	set templatefile [ file join [ hm_info -appinfo SPECIFIEDPATH TEMPLATES_DIR ] feoutput optistruct optistruct ];
	set tmpModelPath "./PreModel_tmp.fem";
	hm_answernext yes;
	*feoutputwithdata $templatefile $tmpModelPath 0 0 2 1 3;
	::hmCreH3d::explog 1 "Exported fme file = $tmpModelPath";

	return 0
}

proc ::hmCreH3d::ReadResult {args} {
	variable analysisValidity;
	variable thicknessValues;
	variable densityValues;

	array set thfile {"omote" "./PreModel3.NEZ" "hojyo" "./PreModel3_hojyo.NEZ" "rimen" "./PreModel3_rimen.NEZ"}
	set analysisList {"omote" "hojyo" "rimen"}
	::hmCreH3d::explog 1 "Start reading all results.";

	foreach analylsis $analysisList {
		set thicknessValues($analylsis) [dict create]
		set densityValues($analylsis) [dict create]

		if !$analysisValidity($analylsis) {
			::hmCreH3d::explog 1 "Skip reading. analylsis = $analylsis";
			continue
		}
		if { [file exists $thfile($analylsis)] == 0 || [file size $thfile($analylsis)] == 0} {
			::hmCreH3d::explog 1 "Analysis result file was not found. Analysis has failed. <$thfile($analylsis)>" 1;
			error 1;
		}
		if {[catch {::hmCreH3d::ReadOneResult $thfile($analylsis) $analylsis} code option]} {
			::hmCreH3d::explog 1 "Reading the analysis result file failed. <$thfile($analylsis)>. $code $option" 1;
			error 1;
		}
	}

	if {[catch {::hmCreH3d::SetSumResults} code option]} {
		::hmCreH3d::explog 1 "Calculation of total value failed. $code $option" 1;
		error 1;
	}

	return 0
}

proc ::hmCreH3d::ReadOneResult { filePath analylsis } {
	variable thicknessValues;
	variable densityValues;

	::hmCreH3d::explog 1 "Start reading nez file... <$filePath>";
	set readMode "None"
	set ft_r [open $filePath r];

	while {![eof $ft_r]} {
		set line [split [string trim [gets $ft_r] ,] ,];
		if { [string first "stack thickness" $line] != -1 } {
			set readMode "thickness"
		} elseif { [string first "current density vector" $line] != -1 } {
			set readMode "density"
		}

		# Skip header
		if {$readMode == "None"} {
			continue;
		}

		# Skip non values
		if {[llength $line] != 2 || ![string is double -strict [lindex $line 0]] || ![string is double -strict [lindex $line 1]]} {
			continue;
		}

		set id [ lindex $line 0 ];
		set value [ lindex $line 1 ];

		# End data
		if { $id == -1 && $value == 0 } {
			set readMode "None";
			continue;
		}

		# Set values
		if {$readMode == "thickness"} {
			dict set thicknessValues($analylsis) $id $value;
		} else {
			dict set densityValues($analylsis) $id $value;
		}
	}

	::hmCreH3d::explog 1 "Number of data ... <thickness: [dict size $thicknessValues($analylsis)] density: [dict size $densityValues($analylsis)]>";
	close $ft_r;

	return 0
}

proc ::hmCreH3d::SetSumResults { args } {
	variable analysisValidity;
	variable thicknessValues;
	variable densityValues;

	set thicknessValues(omotehojyo) [dict create];
	set densityValues(omotehojyo) [dict create];

	set thicknessValues(omoterimen) [dict create];
	set densityValues(omoterimen) [dict create];

	set thicknessValues(omotehojyorimen) [dict create];
	set densityValues(omotehojyorimen) [dict create];

	::hmCreH3d::explog 1 "Start calculating sum of results.";

	# omote + hojyo
	if { $analysisValidity(omotehojyo) } {
		::hmCreH3d::SumResults "omotehojyo" [list omote hojyo]
	}

	# omote + rimen
	if { $analysisValidity(omoterimen) } {
		::hmCreH3d::SumResults "omoterimen" [list omote rimen]
	}

	# omote + hojyo + rimen
	if { $analysisValidity(omotehojyorimen) } {
		::hmCreH3d::SumResults "omotehojyorimen" [list omote hojyo rimen]
	}
}

proc ::hmCreH3d::SumResults { newKey sumList } {
	variable thicknessValues;
	variable densityValues;

	::hmCreH3d::explog 1 "Start calculating sum... <[join $sumList +]>";
	foreach analysis $sumList {
		# thickness
		set nodes [ dict keys $thicknessValues($analysis) ];
		foreach nodeID $nodes {
			set value [dict get $thicknessValues($analysis) $nodeID]
			if {[dict exists $thicknessValues($newKey) $nodeID]} {
				set value [expr {$value + [dict get $thicknessValues($newKey) $nodeID]}];
			}
			dict set thicknessValues($newKey) $nodeID $value
		}

		# density
		set nodes [ dict keys $densityValues($analysis) ];
		foreach nodeID $nodes {
			set value [dict get $densityValues($analysis) $nodeID]
			if {[dict exists $densityValues($newKey) $nodeID]} {
				set value [expr {$value + [dict get $densityValues($newKey) $nodeID]}];
			}
			dict set densityValues($newKey) $nodeID $value
		}
	}

	return 0;
}

proc ::hmCreH3d::OutputText { args } {
	variable analysisValidity;
	variable relatedElements;
	variable relatedNodes;
	::hmCreH3d::explog 1 "Output text files.";

	set analysisList {"omote" "hojyo" "rimen"}
	foreach analylsis $analysisList {
		set relatedElements($analylsis) [list]
		set relatedNodes($analylsis) [list]

		if { !$analysisValidity($analylsis) } {
			continue
		}

		if {[catch {::hmCreH3d::SetRelatedEntities $analylsis} code option]} {
			::hmCreH3d::explog 1 "Failed to get related entity. <${analylsis}>. $code $option" 1;
			error 1;
		}

		if {[catch {::hmCreH3d::OutputTextOneAnalylsis $analylsis} code option]} {
			::hmCreH3d::explog 1 "CSV output failed. <${analylsis}>. $code $option" 1;
			error 1;
		}
	}

	if {[catch {::hmCreH3d::OutputTextSum} code option]} {
		::hmCreH3d::explog 1 "Failed to output total CSV. $code $option" 1;
		error 1;
	}

	return 0
}

proc ::hmCreH3d::SetRelatedEntities { analylsis } {
	variable thicknessValues;
	variable relatedElements;
	variable relatedNodes;
	::hmCreH3d::explog 1 "Find related entities. <analylsis: ${analylsis}>";

	set nList [dict keys $thicknessValues($analylsis)];
	set nList [lsort -real -unique $nList];
	if {[llength $nList] == 0} {
		return 0;
	}

	eval *createmark nodes 1 $nList;
	hm_getcrossreferencedentitiesmark nodes 1 2 2 0 0 -byid;
	set eList [hm_getmark elems 2];

	set nRefList [hm_getvalue elems user_ids=$eList dataname=nodes];
	set elemtypes [hm_getvalue elems user_ids=$eList dataname=config];
	set eList_temp [list];

	for {set i 0} {$i < [llength $eList]} {incr i} {
		if {[lindex $elemtypes $i] < 100 || [lindex $elemtypes $i] >= 200} {
			continue;
		}
		
		set flg 0;
		foreach j [lindex $nRefList $i] {
			if { [lsearch -real -sorted $nList $j] == -1} {
				set flg 1;
				break;
			}
		}
		if { $flg == 0 } {
			lappend eList_temp [lindex $eList $i];
		}
	}

	set relatedElements($analylsis) $eList_temp;
	set relatedNodes($analylsis) [hm_getvalue elems user_ids=$eList dataname=nodes];
	::hmCreH3d::explog 1 "Number of Related entities ... <Node: [llength $relatedNodes($analylsis)] Element: [llength $relatedElements($analylsis)]>";

	return 0
}

proc ::hmCreH3d::OutputTextOneAnalylsis { analylsis } {
	variable thicknessValues;
	variable densityValues;
	variable relatedElements;
	variable relatedNodes;
	::hmCreH3d::explog 1 "Output one analysis. <analylsis: ${analylsis}>";

	set resfile "./temp/ResValList";
	set thicknessFile "${resfile}_${analylsis}_thickness.csv"
	set densityFile "${resfile}_${analylsis}_density.csv"

	# Thickness
	::hmCreH3d::explog 1 "Export information of entities ... <${thicknessFile}>";
	::hmCreH3d::OutputCSV $thicknessFile $relatedElements($analylsis) $relatedNodes($analylsis) $thicknessValues($analylsis);
		
	# Density
	::hmCreH3d::explog 1 "Export information of entities ... <${densityFile}>";
	::hmCreH3d::OutputCSV $densityFile $relatedElements($analylsis) $relatedNodes($analylsis) $densityValues($analylsis) 0;

	return 0;
}

proc ::hmCreH3d::OutputTextSum { args } {
	variable analysisValidity;
	variable thicknessValues;
	variable densityValues;
	variable relatedElements;
	variable relatedNodes;

	set resfile "./temp/ResValList";
	set eList $relatedElements(omote) 
	set nRefList $relatedNodes(omote)

	# omete + hojyo
	if { $analysisValidity(omotehojyo) } {
		::hmCreH3d::explog 1 "Export information of entities ... <${resfile}_omotehojyo_thickness.csv>";
		::hmCreH3d::OutputCSV "${resfile}_omotehojyo_thickness.csv" $eList $nRefList $thicknessValues(omotehojyo);
		::hmCreH3d::explog 1 "Export information of entities ... <${resfile}_omotehojyo_density.csv>";
		::hmCreH3d::OutputCSV "${resfile}_omotehojyo_density.csv"  $eList $nRefList $densityValues(omotehojyo) 0;
	}

	# omete + rimen
	if { $analysisValidity(omoterimen) } {
		::hmCreH3d::explog 1 "Export information of entities ... <${resfile}_omoterimen_thickness.csv>";
		::hmCreH3d::OutputCSV "${resfile}_omoterimen_thickness.csv" $eList $nRefList $thicknessValues(omoterimen);
		::hmCreH3d::explog 1 "Export information of entities ... <${resfile}_omoterimen_density.csv>";
		::hmCreH3d::OutputCSV "${resfile}_omoterimen_density.csv" $eList $nRefList $densityValues(omoterimen) 0;
	}

	# omete + hojyo + rimen
	if { $analysisValidity(omotehojyorimen) } {
		::hmCreH3d::explog 1 "Export information of entities ... <${resfile}_omotehojyorimen_thickness.csv>";
		::hmCreH3d::OutputCSV "${resfile}_omotehojyorimen_thickness.csv" $eList $nRefList $thicknessValues(omotehojyorimen);
		::hmCreH3d::explog 1 "Export information of entities ... <${resfile}_omotehojyorimen_density.csv>";
		::hmCreH3d::OutputCSV "${resfile}_omotehojyorimen_density.csv" $eList $nRefList $densityValues(omotehojyorimen) 0;
	}

	return 0;
}

proc ::hmCreH3d::OutputCSV { filePath eList nRefList dictValues {round 1}} {
	set ft_w [open $filePath w];
	for {set i 0} {$i < [llength $eList]} {incr i} {
		set elementID [lindex $eList $i];
		set allNodesExist 1;
		foreach nodeID [lindex $nRefList $i] {
			if {![dict exists $dictValues $nodeID]} {
				set allNodesExist 0;
				break;
			}
		}
		if {!$allNodesExist} {
			continue
		}
		foreach nodeID [lindex $nRefList $i] {
			set value [dict get $dictValues $nodeID];
			if $round {
				set value [::hmCreH3d::Round $value 7];
			}
			puts $ft_w "$elementID,$nodeID,$value";
		}
	}
	close $ft_w;
	return 0
}

proc ::hmCreH3d::Round { value round } {
    set factor [ expr pow( 10, $round ) ];
    return [ expr round( $value * $factor ) / $factor ];
}

proc ::hmCreH3d::OutputH3D {args} {
	variable analysisValidity;

	::hmCreH3d::explog 1 "Export a header file of h3d ...";

	# export hwascii
	set hwafile "./temp/ResInfo.hwascii";
	set ft_w [open $hwafile w];
	puts $ft_w "ALTAIR ASCII FILE"
	puts $ft_w "\$TITLE = Thickness Result"
	puts $ft_w "\$SUBCASE = 1 Subcase1"
	
	foreach analysis [list "omote" "hojyo" "rimen" "omotehojyo" "omoterimen" "omotehojyorimen"] {
		if { !$analysisValidity($analysis) } {
			continue
		}
		::hmCreH3d::OutputHWAsciiRows $ft_w $analysis;
	}
	close $ft_w;

	::hmCreH3d::explog 1 "Execute the hvtrans ...";

	set hvtr_path [hm_info -appinfo SPECIFIEDPATH hw_readers];
	set modelpath "./PreModel_tmp.fem";
	set h3dfilePath "./temp/masterData.h3d";
	catch {eval exec "\"${hvtr_path}/hvtrans.exe\"" -a "\"${hwafile}\"" "\"${modelpath}\"" -o "\"${h3dfilePath}\""} code option
	::hmCreH3d::explog 1 "Finished hvtrans.exe. $code $option";

	return 0
}

proc ::hmCreH3d::OutputHWAsciiRows {ft_w analysis} {
	set thicknessType "Thick value $analysis"
	set thicknessCSV "ResValList_${analysis}_thickness.csv"

	set densityType "Current Density $analysis"
	set densityCSV "ResValList_${analysis}_density.csv"

	set shortageType "Thick shortage $analysis"
	set shortageCSV "ResValList_${analysis}_shortage_thickness.csv"

	puts $ft_w "\$BINDING = ELEMENT"
	puts $ft_w "\$COLUMN_INFO = ENTITY_ID	GRID_ID"
	puts $ft_w "\$RESULT_TYPE= $thicknessType"
	puts $ft_w "\$TIME =  0.0000"
	puts $ft_w "\$INCLUDE = $thicknessCSV"

	puts $ft_w "\$BINDING = ELEMENT"
	puts $ft_w "\$COLUMN_INFO = ENTITY_ID	GRID_ID"
	puts $ft_w "\$RESULT_TYPE= $densityType"
	puts $ft_w "\$TIME =  0.0000"
	puts $ft_w "\$INCLUDE = $densityCSV"

	return 0;
}

proc ::hmCreH3d::OutputMaxMin {args} {
	variable analysisValidity;
	variable thicknessValues;
	variable relatedNodes;

	if {![hm_entityinfo exist sets "All_DSNodes" -byname]} {
		::hmCreH3d::explog 1 "All_DSNodes not found. Failed in preprocessing." 1;
		error 1;
	}
	if {![hm_entityinfo exist sets "All_PLNodes" -byname]} {
		::hmCreH3d::explog 1 "All_PLNodes not found. Failed in preprocessing." 1;
		error 1;
	}

	set DsList [lsort -real [hm_getvalue sets name="All_DSNodes" dataname=ids]];
	set PlList [lsort -real [hm_getvalue sets name="All_PLNodes" dataname=ids]];

	set resfile "./temp/MaxMinVal.txt";
	set ft_w [open $resfile w];
	puts $ft_w "#AnalysisType,keyType,DSMinNode,DSMinVal,DSMaxNode,DSMaxVal,PLMinNode,PLMinVal,PLMaxNode,PLMaxVal,AverageDS,AverageNotDS"

	foreach analysis [list "omote" "hojyo" "rimen" "omotehojyo" "omoterimen" "omotehojyorimen"] {
		if { !$analysisValidity($analysis) } {
			continue
		}

		set nRefList $relatedNodes(omote)
		if { $analysis in [ list "hojyo" "rimen" ] } {
			set nRefList $relatedNodes($analysis)
		}

		::hmCreH3d::explog 1 "Output Max and Min. <$analysis>";
		::hmCreH3d::OutputMaxMinOne $ft_w $DsList $PlList $analysis "Thick value" $thicknessValues($analysis) $nRefList;
	}
	close $ft_w;

	return 0;
}

proc ::hmCreH3d::OutputMaxMinOne {ft_w DsList PlList analysis keyType valueDict nRefList} {
	# Lists for Ds,Pl-Min,Max
	set DsVals [list];
	set PlVals [list];
	dict for {nodeID value} $valueDict {
		if {[lsearch -real -sorted $DsList $nodeID] != -1} {
			lappend DsVals [ list $nodeID $value ];
		}
		if {[lsearch -real -sorted $PlList $nodeID] != -1} {
			lappend PlVals [ list $nodeID $value ];
		}
	}

	set DsVals [ lsort -real -increasing -index 1 $DsVals ];
	set PlVals [ lsort -real -increasing -index 1 $PlVals ];

	# Ds-Min,Max
	lassign {"" ""} DsMinNodeID DsMinVal;
	lassign {"" ""} DsMaxNodeID DsMaxVal;
	if { [ llength $DsVals ] != 0 } {
		lassign [lindex $DsVals 0] DsMinNodeID DsMinVal;
		lassign [lindex $DsVals end] DsMaxNodeID DsMaxVal;
	}

	# Pl-Min,Max
	lassign {"" ""} PlMinNodeID PlMinVal;
	lassign {"" ""} PlMaxNodeID PlMaxVal;
	if { [ llength $PlVals ] != 0 } {
		lassign [lindex $PlVals 0] PlMinNodeID PlMinVal;
		lassign [lindex $PlVals end] PlMaxNodeID PlMaxVal;
	}

	# List for average
	lassign {"" ""} modelThkDS modelThkNotDs;
	set NIds [lsort -real -unique [string map {\{ "" \} ""} $nRefList]];
	foreach nid $NIds {
		if {![dict exists $valueDict $nid]} {
			continue;
		}
		set value [dict get $valueDict $nid];
		if {[lsearch -real -sorted $DsList $nid] != -1} {
			lappend modelThkDS $value;
		} else {
			lappend modelThkNotDs $value;
		}
	}
	# average
	lassign {0 0} nThkInfoDs nThkInfoNotDs;
	if {[llength $modelThkDS] != 0} {
		set nThkInfoDs [expr {[eval expr [join $modelThkDS "+"]] / ([llength $modelThkDS] * 1.0)}];
	}
	if {[llength $modelThkNotDs] != 0} {
		set nThkInfoNotDs [expr {[eval expr [join $modelThkNotDs "+"]] / ([llength $modelThkNotDs] * 1.0)}];
	}

	puts $ft_w "${analysis},${keyType},${DsMinNodeID},${DsMinVal},${DsMaxNodeID},${DsMaxVal},${PlMinNodeID},${PlMinVal},${PlMaxNodeID},${PlMaxVal},${nThkInfoDs},${nThkInfoNotDs}"
	return 0;
}

proc ::hmCreH3d::OutputNG {args} {
	set resfile "./temp/NGVal.txt";
	set ft_w [open $resfile w];

	set NGGroups [ ::hmCreH3d::GetSetGroups ];
	foreach NGroup $NGGroups {
		::hmCreH3d::explog 1 "Output NG. <$NGGroups>";
		::hmCreH3d::OutputNGOneGroup $ft_w $NGroup;
	}
	close $ft_w
	return 0;
}

proc ::hmCreH3d::GetSetGroups {args} {
	set keyName "Green"
	set index 0;
	set DSPLList [list];

	while {1} {
		set index [expr {$index + 1}];
		set DSName "${keyName}${index}_DSNodes"
		set PLName "${keyName}${index}_PLNodes"
		if {![hm_entityinfo exist sets $DSName -byname] || ![hm_entityinfo exist sets $PLName -byname]} {
			break;
		}
		lappend DSPLList [list $DSName $PLName]
	}
	return $DSPLList;
}

proc ::hmCreH3d::OutputNGOneGroup {ft_w NGroup} {
	variable thresholdUpperLimitDS;
	variable thresholdUpperLimitPL;

	lassign $NGroup DSName PLName;

	set DSAreas [::hmCreH3d::GetNGAreas $DSName];
	::hmCreH3d::OutputNGOneKey $ft_w "DS" $DSAreas $thresholdUpperLimitDS;

	set PLAreas [::hmCreH3d::GetNGAreas $PLName];
	::hmCreH3d::OutputNGOneKey $ft_w "PL" $PLAreas $thresholdUpperLimitPL;
}

proc ::hmCreH3d::GetNGAreas {setName} {
	variable thicknessEvaluationPitch;

	set nodeList [lsort -real [hm_getvalue sets name=$setName dataname=ids]];

	# get yz range
	set result [::hmCreH3d::GetMinMaxYZ $nodeList];
	if { [ llength $result ] == 0 } {
		return [];
	}
	lassign $result minY maxY minZ maxZ;

	# diviede ndoes to (Y,Z) area
	set distance $thicknessEvaluationPitch;
	set areaNodes [ dict create ]
	foreach nodeID $nodeList {
		eval lassign [ hm_nodevalue $nodeID ] x y z;
		set nY [expr {int(($y - $minY) / $distance)}];
		set nZ [expr {int(($z - $minZ) / $distance)}];
		dict lappend areaNodes "${nY}_${nZ}" $nodeID;
	}

	# diviede one area to sub 4 area
	set subAreaNodes [dict create]
	dict for {area nodes} $areaNodes {
		set result [::hmCreH3d::GetMinMaxYZ $nodes];
		if { [ llength $result ] == 0 } {
			continue;
		}

		lassign $result tminY tmaxY tminZ tmaxZ;
		set midY [expr {0.5 * ($tminY + $tmaxY)}];
		set midZ [expr {0.5 * ($tminZ + $tmaxZ)}];

		foreach nodeID $nodes {
			eval lassign [ hm_nodevalue $nodeID ] x y z;
			if {$y < $midY && $z < $midZ} {
				set nSub 0;
			} elseif {$y >= $midY && $z < $midZ} {
				set nSub 1;				
			} elseif {$y < $midY && $z >= $midZ} {
				set nSub 2;
			} else {
				set nSub 3;
			}
			dict lappend subAreaNodes "${area}_${nSub}" $nodeID;
		}
	}
	return $subAreaNodes;
}

proc ::hmCreH3d::GetMinMaxYZ {nodeList} {
	lassign {"" "" "" ""} minY maxY minZ maxZ;
	foreach nodeID $nodeList {
		eval lassign [ hm_nodevalue $nodeID ] x y z;
		if {$minY == "" || $minY > $y} {
			set minY $y;
		}
		if {$maxY == "" || $maxY < $y} {
			set maxY $y;
		}
		if {$minZ == "" || $minZ > $z} {
			set minZ $z;
		}
		if {$maxZ == "" || $maxZ < $z} {
			set maxZ $z;
		}
	}
	if {$minY == "" || $maxY == "" || $minZ == "" || $maxZ == ""} {
		return [];
	}
	return [list $minY $maxY $minZ $maxZ];
}

proc ::hmCreH3d::OutputNGOneKey {ft_w keyType areas thresholdUpperLimit} {
	variable analysisValidity;
	variable thresholdLowerLimit
	variable thicknessValues;

	foreach analysis [list "omote" "hojyo" "rimen" "omotehojyo" "omoterimen" "omotehojyorimen"] {
		if { !$analysisValidity($analysis) } {
			continue
		}

		# 過剰：上限値より大きい膜厚値をNGとして出力
		::hmCreH3d::OutputNGOneDict $ft_w $analysis $keyType "Thick value" $areas $thicknessValues($analysis) $thresholdUpperLimit;

		# 不足：下限値より小さい膜厚値をNGとして出力
		::hmCreH3d::OutputNGOneDict $ft_w $analysis $keyType "Thick shortage" $areas $thicknessValues($analysis) $thresholdLowerLimit;
	}
}

proc ::hmCreH3d::OutputNGOneDict {ft_w analysis keyType0 keyType1 areas valueDict threshold} {
	set base [expr {$threshold * 1.0E-6}];

	dict for {area nodes} $areas {
		lassign {"" "" "" ""} maxNodeID maxValue minNodeID minValue;
		foreach nodeID $nodes {
			if {![dict exists $valueDict $nodeID]} {
				continue;
			}
			set value [dict get $valueDict $nodeID];
			if {$maxValue == "" || $maxValue < $value} {
				set maxValue $value;
				set maxNodeID $nodeID;
			}
			if {$minValue == "" || $minValue > $value} {
				set minValue $value;
				set minNodeID $nodeID;
			}
		}

		if {$keyType1 == "Thick value"} {
			# 過剰：上限値より小さければスキップ
			if {$maxValue == ""} {
				continue;
			}
			if {$maxValue < $base} {
				continue;
			}
			# NGテキストに出力
			puts $ft_w "${analysis},${keyType0},${keyType1},${area},${maxNodeID},${maxValue}";
		} else {
			# 過剰：下限値より大きければスキップ
			if {$minValue == ""} {
				continue;
			}
			if {$minValue > $base} {
				continue;
			}
			# NGテキストに出力
			puts $ft_w "${analysis},${keyType0},${keyType1},${area},${minNodeID},${minValue}";
		}
	}
}

proc ::hmCreH3d::OutputMaxOnRimen {args} {
	variable analysisValidity;
	variable thicknessValues;
	variable rimenStructureEvaluation;

	if {!$rimenStructureEvaluation} {
		return 0;
	}

	set dictValues [dict create];
	foreach analysis [list "omotehojyorimen" "omoterimen" "omotehojyo" "omote" ] {
		if {!$analysisValidity($analysis)} {
			continue;
		}
		set dictValues $thicknessValues($analysis)
		break;
	}

	set resfile "./temp/RimenMaxVal.txt";
	set ft_w [open $resfile w];

	set RimenGroups [ ::hmCreH3d::GetRimenMaxSetGroups ];
	foreach RimenGroup $RimenGroups {
		::hmCreH3d::explog 1 "Output max value on Rimen. <$RimenGroup>";
		::hmCreH3d::OutputMaxOnRimenOneGroup $ft_w $RimenGroup $dictValues;
	}
	close $ft_w
	return 0;
}

proc ::hmCreH3d::GetRimenMaxSetGroups {args} {
	set prefix "CustomColor";

	*createmark sets 1 all;
	if { [hm_marklength sets 1] == 0 } {
		return [];
	}

	# gets custom color set
	set CustomColorSetList [list];
	set setIDList [ hm_getmark sets 1 ];
	foreach setID $setIDList {
		set setName [hm_getvalue sets id=$setID dataname=name]
		if {![string match -nocase "${prefix}*" $setName]} {
			continue;
		}
		
		lappend CustomColorSetList $setName;
	}
	
	return $CustomColorSetList;
}

proc ::hmCreH3d::OutputMaxOnRimenOneGroup {ft_w group dictValues} {
	set maxNodeID "";
	set maxValue "";

	set nodeList [hm_getvalue sets name=$group dataname=ids];
	foreach nodeID $nodeList {
		if {![dict exists $dictValues $nodeID]} {
			continue;
		}
		
		set value [dict get $dictValues $nodeID];
		if {$maxValue == "" || $maxValue < $value} {
			set maxNodeID $nodeID;
			set maxValue $value
		}
	}

	if {$maxNodeID == ""} {
		return 0;
	}

	puts $ft_w "${group},${maxNodeID},${maxValue}";
	return 0;
}

::hmCreH3d::main;
