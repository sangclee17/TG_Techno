namespace eval ::hvCreDt {
	variable setinfo;
	variable scriptFolder;
	set scriptFolder [info script]
}

#####
proc ::hvCreDt::main {args} {
	::hvCreDt::explog 1 "##### HV script #####";

	if {[catch {::hvCreDt::ReadAnalysisConditions} code option]} {
		::hvCreDt::explog 1 "Error ReadAnalysisConditions: $code $option" 1;
		::hvCreDt::errfile;
		return 1;
	}

	if {[catch {::hvCreDt::ReadNoteIniFile} code option]} {
		::hvCreDt::explog 1 "Error ReadNoteIniFile: $code $option>" 1;
		::hvCreDt::errfile;
		return 1;
	}

	if {[catch {::hvCreDt::Initialize} code option]} {
		::hvCreDt::explog 1 "Error Initialize: $code $option>" 1;
		::hvCreDt::errfile;
		return 1;
	}

	if {[catch {::hvCreDt::ReadModel} code option]} {
		::hvCreDt::explog 1 "Error ReadModel: $code $option>" 1;
		::hvCreDt::errfile;
		return 1;
	}

	if {[catch {::hvCreDt::SetDisplayName} code option]} {
		::hvCreDt::explog 1 "Error SetDisplayName: $code $option>" 1;
		::hvCreDt::errfile;
		return 1;
	}

	if {[catch {::hvCreDt::ExportH3DAndImage} code option]} {
		::hvCreDt::explog 1 "Error ExportH3DAndImage: $code $option>" 1;
		::hvCreDt::errfile;
		return 1;
	}

	::hvCreDt::explog 1 "End HV script.";
	return 0;
}

#####
proc ::hvCreDt::Initialize {args} {
	variable setinfo;
	variable pageHeight;
	variable pageWidht;

	# output directory
	if {[file isdirectory ./result] == 1} {
		catch {file delete -force ./result} res;
	}
	catch {file mkdir ./result} res;

	# delete old error file
	if {[file isfile ./Errorflg] == 1} {
		catch {file delete -force ./Errorflg} res;
	}

	set t [::post::GetT];
	hwi OpenStack;
	
	hwi GetSessionHandle ss$t;
	::hvCreDt::explog 1 "HV Start...";

	set nEx [ expr { $setinfo(legNumExcess) - 10 } ]
	set nSh [ expr { $setinfo(legNumShortage) - 6 } ]
	set nH $nEx
	if {$nEx > $nSh} {
		set nH $nSh
	}

	set pageWidht [ss$t GetPageWidth];
	set pageHeight [ss$t GetPageHeight];
	set hLen [expr {$nH * 20 + 300}];
	set wLen 135;
	hwi CloseStack;

	if { $pageHeight <= $hLen || $pageWidht <= $wLen } {
		::hvCreDt::explog 1 "Graphics area is unexpectedly small. w:$pageHeight h:$pageWidht" 1;
		error 1
	}

	return 0;
}

##### 
proc ::hvCreDt::ReadNoteIniFile {args} {
	variable scriptFolder;
	variable noteAttribute;

	set noteAttribute [dict create]
	dict set noteAttribute "Max_DS_BorderColor" {255 0 0};
	dict set noteAttribute "Max_DS_TextColor" {0 0 0};
	dict set noteAttribute "Max_DS_BGColor" {255 255 255};
	dict set noteAttribute "Max_DS_BorderThickness" 5;
	dict set noteAttribute "Max_DS_FontSize" 25;

	dict set noteAttribute "Max_PL_BorderColor" {255 0 0};
	dict set noteAttribute "Max_PL_TextColor" {252 252 252};
	dict set noteAttribute "Max_PL_BGColor" {132 161 214};
	dict set noteAttribute "Max_PL_BorderThickness" 5;
	dict set noteAttribute "Max_PL_FontSize" 25;

	dict set noteAttribute "Max_NG_DS_BorderColor" {0 0 0};
	dict set noteAttribute "Max_NG_DS_TextColor" {0 0 0};
	dict set noteAttribute "Max_NG_DS_BGColor" {255 255 255};
	dict set noteAttribute "Max_NG_DS_BorderThickness" 1;
	dict set noteAttribute "Max_NG_DS_FontSize" 12;

	dict set noteAttribute "Max_NG_PL_BorderColor" {0 0 0};
	dict set noteAttribute "Max_NG_PL_TextColor" {252 252 252};
	dict set noteAttribute "Max_NG_PL_BGColor" {132 161 214};
	dict set noteAttribute "Max_NG_PL_BorderThickness" 1;
	dict set noteAttribute "Max_NG_PL_FontSize" 12;

	dict set noteAttribute "Min_DS_BorderColor" {255 0 0};
	dict set noteAttribute "Min_DS_TextColor" {0 0 0};
	dict set noteAttribute "Min_DS_BGColor" {255 255 255};
	dict set noteAttribute "Min_DS_BorderThickness" 5;
	dict set noteAttribute "Min_DS_FontSize" 25;

	dict set noteAttribute "Min_PL_BorderColor" {255 0 0};
	dict set noteAttribute "Min_PL_TextColor" {252 252 252};
	dict set noteAttribute "Min_PL_BGColor" {132 161 214};
	dict set noteAttribute "Min_PL_BorderThickness" 5;
	dict set noteAttribute "Min_PL_FontSize" 25;

	dict set noteAttribute "Min_NG_DS_BorderColor" {0 0 0};
	dict set noteAttribute "Min_NG_DS_TextColor" {0 0 0};
	dict set noteAttribute "Min_NG_DS_BGColor" {255 255 255};
	dict set noteAttribute "Min_NG_DS_BorderThickness" 1;
	dict set noteAttribute "Min_NG_DS_FontSize" 12;

	dict set noteAttribute "Min_NG_PL_BorderColor" {0 0 0};
	dict set noteAttribute "Min_NG_PL_TextColor" {252 252 252};
	dict set noteAttribute "Min_NG_PL_BGColor" {132 161 214};
	dict set noteAttribute "Min_NG_PL_BorderThickness" 1;
	dict set noteAttribute "Min_NG_PL_FontSize" 12;

	dict set noteAttribute "Rimen_BorderColor" {0 0 0};
	dict set noteAttribute "Rimen_TextColor" {0 0 0};
	dict set noteAttribute "Rimen_BGColor" {255 255 255};
	dict set noteAttribute "Rimen_BorderThickness" 1;
	dict set noteAttribute "Rimen_FontSize" 12;

	set dirName [file dirname $scriptFolder];
	set ymlFile [file join $dirName "note.csv"];
	if {![file isfile $ymlFile]} {
		::hvCreDt::explog 1 "Use default setting, because there is no configuration file(note.yml)";
		return 0;
	}

	set fp [open "$ymlFile" r];
	while {! [eof $fp]} {
		set line [string trim [gets $fp]];
		set values [ split $line "," ];
		if { [ llength $values ] != 2} {
			continue
		}

		set key [ lindex $values 0 ];
		set value [ lindex $values 1 ];
		dict set noteAttribute $key $value;
	}
	close $fp;

	return 0;
}

##### 
proc ::hvCreDt::ReadAnalysisConditions {args} {
	variable setinfo;

	array set setinfo {"legNumExcess" 10 "legMaxExcess" 0.0001 "legMinExcess" 0 \
		"legNumShortage" 6 "legMaxShortage" 0.00003 "legMinShortage" 0\
		 "RhoVal" 8900 "CADNAME" "" "Comment" "" "rimenStructureEvaluation" 0};

	set spath "./analysis_conditions.txt";
	if {[file exists $spath] == 0 } {
		::hvCreDt::explog 1 "Analysis condition file was not found." 1;
		error 1;
	}
	
	set chid [open "${spath}" r];
	while {! [eof $chid]} {
		set line [string trim [gets $chid]];
		set lines [ split $line ":" ];
		if { [ llength $lines ] < 2 } {
			continue;
		}

		set key [ lindex $lines 0 ]
		set value [ lindex $lines 1 ]
		
		if { $key  == "A067" } {
			if {[string is integer -strict $value] == 1} {
				set setinfo(legNumExcess) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of legend num for excess.";
				set setinfo(legNumExcess) 10;
			}
		} elseif { $key  == "A068" } {
			if {[string is double -strict $value] == 1} {
				set setinfo(legMaxExcess) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of legend max for excess.";
				set setinfo(legMaxExcess) 0.0001;
			}
		} elseif { $key  == "A069" } {
			if {[string is double -strict $value] == 1} {
				set setinfo(legMinExcess) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of legend min for excess.";
				set setinfo(legMinExcess) 0;
			}
		} elseif { $key  == "A070" } {
			if {[string is double -strict $value] == 1} {
				set setinfo(legNumShortage) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of legend num for shortage.";
				set setinfo(legNumShortage) 6;
			}
		} elseif { $key  == "A071" } {
			if {[string is double -strict $value] == 1} {
				set setinfo(legMaxShortage) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of legend max for shortage.";
				set setinfo(legMaxShortage) 0.00003;
			}
		} elseif { $key  == "A072" } {
			if {[string is double -strict $value] == 1} {
				set setinfo(legMinShortage) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of legend min for shortage.";
				set setinfo(legMinShortage) 0;
			}
		} elseif { $key  == "E055" } {
			if {[string is double -strict $value] == 1} {
				set setinfo(RhoVal) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of Rho value.";
				set setinfo(RhoVal) 8900;
			}
		} elseif { $key  == "A007" } {
			if {[string is ascii -strict $value] == 1} {
				set setinfo(CADNAME) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of CAD name.";
				set setinfo(CADNAME) "";
			}
		} elseif { $key  == "A063" } {
			if {[string is ascii -strict $value] == 1} {
				set setinfo(Comment) $value;
			} else {
				::hvCreDt::explog 1 "Can not get information of Comment.";
				set setinfo(Comment) "";
			}
		} elseif { $key  == "A066" } {
			if {[string is boolean -strict $value] == 1} {
				if {$value} {
					set setinfo(rimenStructureEvaluation) 1;					
				} else {
					set setinfo(rimenStructureEvaluation) 0;
				}
			} else {
				::hvCreDt::explog 1 "Can not get information of Rimen structure evaluation.";
				set setinfo(rimenStructureEvaluation) 0;
			}
		}
	}
	close $chid;
	::hvCreDt::explog 1 "Legend excess=($setinfo(legNumExcess), $setinfo(legMinExcess), $setinfo(legMaxExcess)),\
		Legend shortage=($setinfo(legNumShortage), $setinfo(legMinShortage), $setinfo(legMaxShortage)),\
		Rho=$setinfo(RhoVal), CADNAME=$setinfo(CADNAME), Comment=$setinfo(Comment),\
		RimenStructureEvaluation=$setinfo(rimenStructureEvaluation)";

	return 0;
}

#####
proc ::hvCreDt::ReadModel {args} {
	set t [::post::GetT];
	hwi OpenStack;

	set mfile "./temp/masterData.h3d";
	if { $mfile == "" } {
		::hvCreDt::explog 1 "masterData.h3d was not found. Failed in previous HyperMesh." 1;
		error -1;
	};

	::post::GetPostHandle p$t;
	p$t GetModelHandle m$t [p$t AddModel $mfile];
	m$t SetResult $mfile;
	
	::hvCreDt::explog 1 "Finished to read file. <[file tail $mfile]>";
	hwi CloseStack;
	return 0;
}

#####
proc ::hvCreDt::SetDisplayName {args} {
	variable setinfo;

	set t [::post::GetT];
	hwi OpenStack;

	::post::GetPostHandle p$t;
	if {[lsearch [p$t GetNoteList] 1] != -1} {
		p$t GetNoteHandle n1$t 1;
		n1$t SetVisibility false;
	}
	
	if {$setinfo(CADNAME) != ""} {
		p$t GetNoteHandle nt$t [p$t AddNote];
		nt$t SetLabel "Model Name";
		nt$t SetText $setinfo(CADNAME);
		nt$t SetPosition topright;
		nt$t SetAttachment window;
		nt$t SetBorderThickness 0;
		nt$t SetVisibility true;
		
		nt$t GetFontHandle ft$t;
		ft$t SetWeight bold;
	}
	::post::Draw;
	
	::hvCreDt::explog 1 "Display model name.";
	hwi CloseStack;
	return 0;
}

proc ::hvCreDt::ExportH3DAndImage {args} {
	# 各解析の出力
	if { [catch {::hvCreDt::ExportH3DAndImageOneAnalysis} code option ] } {
		::hvCreDt::explog 1 "Error ExportH3DAndImageOneAnalysis. $code $option" 1;
		error 1;
	}

	# 裏面構造解析の出力
	if { [catch {::hvCreDt::ExportH3DAndImageRimenStructureEvaluation} code option ] } {
		::hvCreDt::explog 1 "Error ExportH3DAndImageBackSide. $code $option" 1;
		error 1;
	}
}

proc ::hvCreDt::ExportH3DAndImageOneAnalysis {args} {
	variable setinfo;

	set fPath "./result/";
	set iPath "./temp/";
	array set fName {{Current Density} d {Thick value} t {Thick shortage} s};
	::hw::ViewZYFront

	foreach resultType [list "Thick value" "Current Density" "Thick shortage"] {
		foreach analysisType [ list "omote" "hojyo" "rimen" "omotehojyo" "omoterimen" "omotehojyorimen" ] {
			set JPGPath "${iPath}[string map {" " "_"} "$resultType $analysisType"].jpg";
			set H3DPath "${fPath}[string map {" " "_"} "$resultType $analysisType"].h3d";

			# コンター図で利用するデータタイプ。ただしThick shortageのデータはないのでThick valueを利用する
			set contourType "$resultType $analysisType";
			if {$resultType == "Thick shortage"} {
				set contourType "Thick value $analysisType";
			}

			if {![::hvCreDt::HasDataType $contourType]} {
				continue;
			}
			::hvCreDt::explog 1 "Start working <$contourType>";

			# コンター表示
			if { [catch {::hvCreDt::ChgContour "${contourType}"} res ] } {error 1};
			
			# レジェンドの個数、最小、最大
			set legMin $setinfo(legMinExcess);
			set legMax $setinfo(legMaxExcess);
			set legNum $setinfo(legNumExcess);
			if {$resultType == "Thick shortage"} {
				set legMin $setinfo(legMinShortage);
				set legMax $setinfo(legMaxShortage);
				set legNum $setinfo(legNumShortage);
			}
			if { [catch {::hvCreDt::Chglgd 1 $legMin $legMax $legNum} res ] } {error 1};

			# 精度
			if {$resultType == "Thick value" || $resultType == "Thick shortage"} {
				if { [catch {::hvCreDt::Chglgd 2 "" "" "" 2} res ] } {error 1};
			} else {
				if { [catch {::hvCreDt::Chglgd 2 "" "" "" 3} res ] } {error 1};
			}

			# コンターの表示、コンターを持つ要素のみ表示、背景白
			if { [catch {::hvCreDt::ChgContour $contourType 1} res ] } {error 1};
			if { [catch {::hvCreDt::SetMask 2} res ] } {error 1};
			if { [catch {::hvCreDt::SetMask 0} res ] } {error 1};
			if { [catch {::hvCreDt::ChgBgColor 1} res ] } {error 1};

			# 過剰と不足はNoteを付ける、画像も出力する
			if { $resultType == "Thick value" || $resultType == "Thick shortage" } {
				# Noteを作成する（内部でYZ平面でNoteが重複しないように位置を調整している）
				if { [catch {::hvCreDt::CreateAnnotation $resultType $analysisType} code option] } {
					::hvCreDt::explog 1 "Error CreateAnnotation. $code $option" 1;
					error 1;
				}

				# 2Dイメージを出力する
				if { [catch {::hvCreDt::CtrDisp 0} res ] } {error 1 };
				::hvCreDt::explog 1 "Export image <$JPGPath>";
				if { [catch {::hvCreDt::CreCapture $JPGPath} code option] } {
					::hvCreDt::explog 1 "Error CreCapture. $code $option" 1;
					error 1;
				}

				# 2DではNoteが被らないようにしたが、3Dでは回転できるので、Noteは節点に着くように更新する
				if { [catch {::hvCreDt::MoveAnnotationToNode } code option ] } {
					::hvCreDt::explog 1 "Error MoveAnnotationToNode. $code $option" 1;
					error 1;
				}
			}

			# H3Dの出力
			if { [catch {::hvCreDt::CtrDisp 1} res ] } {error 1 };
			if { [catch {::hvCreDt::ExportH3D $H3DPath } code option] } {
				::hvCreDt::explog 1 "Error ExportH3D. $code $option" 1;
				error 1;
			}

			if { [catch {::hvCreDt::ChgBgColor 0} res ] } {error 1};
			if { [catch {::hvCreDt::ChgContour $contourType} res ] } {error 1};

			::hvCreDt::DeleteAnnotation;
			::hvCreDt::CtrDisp 1;
			::hvCreDt::SetMask 2;
			::hvCreDt::Chglgd 0;
		}
	}

	return 0;
}

#####
proc ::hvCreDt::ExportH3DAndImageRimenStructureEvaluation {args} {
	variable setinfo;

	#　裏面構造解析なしなら何もしない
	if {!$setinfo(rimenStructureEvaluation)} {
		return 0;
	}

	# 裏面構造評価で見せるのは、メインの解析結果の図
	# 　主と補助と裏面がON　→　主、主＋補助、主＋裏面、主＋補助＋裏面の結果がある。主＋補助＋裏面でbreakする
	# 　主と補助がON, 裏面がOFF　→　主、主＋補助の結果がある。主＋補助でbreakする
	# 　主と裏面がON, 補助がOFF　→　主、主＋裏面の結果がある。主＋裏面でbreakする
	# 　主がON, 補助と裏面がOFF　→　主 →　主の結果がある。主でbreakする
	# 　それ以外　→　見つからない
	set contourType "";
	foreach type [ list "Thick value omotehojyorimen" "Thick value omoterimen" "Thick value omotehojyo"  "Thick value omote"] {
		if {[::hvCreDt::HasDataType $type]} {
			set contourType $type;
			break;
		}	
	}
	if {$contourType == ""} {
		return 0;
	}

	set fPath "./result/";
	set iPath "./temp/";
	set JPGPath "${iPath}Rimen_structure_evaluation.jpg";
	set H3DPath "${fPath}Rimen_structure_evaluation.h3d";

	#　裏面から見たコンター図
	::hw::ViewZYRear;
	if { [catch {::hvCreDt::ChgContour "${contourType}"} res ] } {error 1};
			
	# レジェンドの個数、最小、最大は過剰を利用
	set legMin $setinfo(legMinExcess);
	set legMax $setinfo(legMaxExcess);
	set legNum $setinfo(legNumExcess);
	if { [catch {::hvCreDt::Chglgd 1 $legMin $legMax $legNum} res ] } {error 1};

	# 精度
	if { [catch {::hvCreDt::Chglgd 2 "" "" "" 2} res ] } {error 1};

	# コンターの表示、コンターを持つ要素のみ表示、背景白
	if { [catch {::hvCreDt::ChgContour $contourType 1} res ] } {error 1};
	if { [catch {::hvCreDt::SetMask 2} res ] } {error 1};
	if { [catch {::hvCreDt::SetMask 0} res ] } {error 1};
	if { [catch {::hvCreDt::ChgBgColor 1} res ] } {error 1};

	# 面ごとにMax値のNoteを作る
	if { [catch {::hvCreDt::CreateRimenMaxNotes} code option ] } {
		::hvCreDt::explog 1 "Error CreateRimenMaxNotes. $code $option" 1;
		error 1;
	}

	# 2Dイメージを出力する
	if { [catch {::hvCreDt::CtrDisp 0} res ] } {error 1 };
	::hvCreDt::explog 1 "Export image <$JPGPath>";
	if { [catch {::hvCreDt::CreCapture $JPGPath} code option ] } {
		::hvCreDt::explog 1 "Error CreCapture. $code $option" 1;
		error 1;
	}

	# Noteは節点に着くように更新する
	if { [catch {::hvCreDt::MoveAnnotationToNode } code option ] } {
		::hvCreDt::explog 1 "Error MoveAnnotationToNode. $code $option" 1;
		error 1;
	}

	# H3Dの出力
	if { [catch {::hvCreDt::CtrDisp 1} res ] } {error 1 };
	if { [catch {::hvCreDt::ExportH3D $H3DPath } code option ] } {
		::hvCreDt::explog 1 "Error ExportH3D. $code $option" 1;
		error 1;
	}

	if { [catch {::hvCreDt::ChgBgColor 0} res ] } {error 1};
	if { [catch {::hvCreDt::ChgContour $contourType} res ] } {error 1};			

	::hvCreDt::DeleteAnnotation;
	::hvCreDt::CtrDisp 1;
	::hvCreDt::SetMask 2;
	::hvCreDt::Chglgd 0;

	return 0;
}

#####
proc ::hvCreDt::CreateRimenMaxNotes {args} {
	variable annotationNotes;
	variable noteArea;
	variable noteAttribute;

	set mfile "./temp/RimenMaxVal.txt";
	if { ![file isfile $mfile]} {
		error 1;
	}

	if {![info exists annotationNotes]} {
		set annotationNotes [dict create]];
		set noteArea [list]
	}

	set bdColor [dict get $noteAttribute "Rimen_BorderColor"]
	set textColor [dict get $noteAttribute "Rimen_TextColor"]
	set bgColor [dict get $noteAttribute "Rimen_BGColor"]
	set bdThickness [dict get $noteAttribute "Rimen_BorderThickness"]
	set fontSize [dict get $noteAttribute "Rimen_FontSize"]

	set chid [open "${mfile}" r];
	while {! [eof $chid]} {
		set line [string trim [gets $chid]];
		set values [ split $line "," ];
		if { [llength $values] != 3 } {
			continue;
		}

		lassign $values setName nodeID maxValue;

		# 0.01umで四捨五入
		set maxValueRound [::hvCreDt::Round $maxValue 7];

		# 四捨五入
		set maxValueInt [expr {int(round($maxValueRound * 1E6))}];
		::hvCreDt::CreateNote $nodeID $maxValueInt $bdColor $textColor $bgColor $fontSize $bdThickness;
		
		#puts "Rimen = $maxValue -> $maxValueRound -> $maxValueInt"
	}

	return 0;
}

#####
proc ::hvCreDt::HasDataType {dataType} {
	set t [::post::GetT];
	hwi OpenStack;
	
	::post::GetActiveModelHandle m$t;
	m$t GetResultCtrlHandle r$t;
	
	set subId [r$t GetCurrentSubcase];
	set resList [r$t GetDataTypeList $subId];
	hwi CloseStack;
	
	if { [lsearch $resList $dataType] != -1 } {
		return 1
	}
	return 0
}

#####
proc ::hvCreDt::ChgContour {{type ""} {avgMd 0} {cdType 0} args} {
	set t [::post::GetT];
	hwi OpenStack;
	
	::post::GetActiveModelHandle m$t;
	m$t GetResultCtrlHandle r$t;
	
	set subId [r$t GetCurrentSubcase];
	set resList [r$t GetDataTypeList $subId];
	
	if { [lsearch $resList $type] != -1 } {
		r$t GetContourCtrlHandle c$t;
		set simNum [r$t GetNumberOfSimulations $subId];
		
		c$t SetDataType $type;
		c$t SetDataComponent {Scalar value};
		c$t SetResultSystem 0;
		if { $cdType == 0 } {
			c$t SetCornerDataEnabled true;
		} else {
			c$t SetCornerDataEnabled false;
		}
		
		if {$avgMd == 1} {
			c$t SetAverageMode simple;
		} else {
			c$t SetAverageMode none;
		}
		r$t SetCurrentSimulation [expr $simNum - 1];
		
		::post::GetPostHandle p$t;
		c$t SetEnableState true;
		p$t SetDisplayOptions contour true;
		p$t SetDisplayOptions legend true;
	} else {
		::hvCreDt::explog 1 "Error Can't find contour type. <$type>" 1;
	}
	::post::Draw;
	hwi CloseStack;
	return 0;
}

#####
proc ::hvCreDt::Chglgd {{flg 0} {min 0} {max 100} {num 9} {preNum 3} args} {
	variable legNum;
	set t [::post::GetT];
	hwi OpenStack;
	
	::post::GetActiveModelHandle m$t;
	m$t GetResultCtrlHandle r$t;
	r$t GetContourCtrlHandle c$t;
	c$t GetLegendHandle l$t;
	
	if { $flg == 0 } {
		l$t Reset;
		
		l$t GetTitleAttributeHandle tt$t;
		tt$t SetVisibility true;
		
	} elseif { $flg == 1 } {
		l$t SetNumberOfColors $num;
		l$t OverrideValue 0 $min;
		l$t OverrideValue $num $max;
		
		l$t GetTitleAttributeHandle tt$t;
		tt$t SetVisibility true;
		
		for {set i 0} {$i <= [l$t GetNumberOfColors]} {incr i} {
			set legNum($i) [format %.f [expr 1000000 * [l$t GetValue $i]]];
			l$t SetColor $i [::hvCreDt::GetColor l$t $num $i];
		}
		catch {::hvCreDt::expleg} res;
		
	} elseif { $flg == 2 && $preNum <= 12 } {
		l$t SetNumericPrecision $preNum;
		
	} elseif { $flg == 3 } {
		l$t SetHeader {[mm]};
		l$t GetHeaderAttributeHandle hh$t;
		hh$t SetVisibility true;
		
		l$t GetTitleAttributeHandle tt$t;
		tt$t SetVisibility false;
		
		l$t SetMinMaxVisibility False entity;
	}
	
	::post::Draw;
	hwi CloseStack;
	return 0;
}

#####
proc ::hvCreDt::GetColor {lt num i} {
	set RGB {255 0 0};
	switch $num {
		10 {
			switch $i {
				0  {set RGB [list 255 0 255]}
				1  {set RGB [list 150 50 255]}
				2  {set RGB [list 0 0 255]}
				3  {set RGB [list 0 170 240]}
				4  {set RGB [list 0 255 255]}
				5  {set RGB [list 100 255 150]}
				6  {set RGB [list 0 255 0]}
				7  {set RGB [list 255 255 0]}
				8  {set RGB [list 255 155 0]}
				9  {set RGB [list 255 0 0]}
				10 {set RGB [ $lt GetColor $i]}
			}
		}
		8 {
			switch $i {
				0  {set RGB [list 255 0 255]}
				1  {set RGB [list 0 0 255]}
				2  {set RGB [list 0 170 240]}
				3  {set RGB [list 0 255 255]}
				4  {set RGB [list 0 255 0]}
				5  {set RGB [list 100 255 150]}
				6  {set RGB [list 255 155 0]}
				7  {set RGB [list 255 0 0]}
				8 {set RGB [ $lt GetColor $i]}
			}
		}
		6 {
			switch $i {
				0  {set RGB [list 255 0 255]}
				1  {set RGB [list 0 0 255]}
				2  {set RGB [list 0 255 255]}
				3  {set RGB [list 0 255 0]}
				4  {set RGB [list 255 255 0]}
				5  {set RGB [list 255 0 0]}
				6 {set RGB [ $lt GetColor $i]}
			}
		}
		5 {
			switch $i {
				0  {set RGB [list 255 0 255]}
				1  {set RGB [list 0 0 255]}
				2  {set RGB [list 0 255 0]}
				3  {set RGB [list 255 255 0]}
				4  {set RGB [list 255 0 0]}
				5 {set RGB [ $lt GetColor $i]}
			}
		}
		default {
			set RGB [ $lt GetColor $i];
		}
	}

	return $RGB
}

#####
proc ::hvCreDt::SetMask {{flg 0} args} {
	set t [::post::GetT];
	hwi OpenStack;
	
	::post::GetActiveModelHandle m$t;
	if { $flg == 0 } {
		
		# undisplay
		set id [m$t AddSelectionSet element];
		m$t GetSelectionSetHandle sl$t $id;
		sl$t Add "contour noresult";
		sl$t Add "dimension 0";
		sl$t Add "dimension 1";
		sl$t Add "dimension 3";
		m$t Mask $id;
		m$t RemoveSelectionSet $id;
		
	} elseif { $flg == 1 } {
		m$t MaskAll;
	} else {
		# display
		m$t UnMaskAll;
	}
	
	::post::Draw;
	hwi CloseStack;
	return 0;
}

#####
proc ::hvCreDt::ChgBgColor {{flg 0} args} {
	variable hyperViewColor;

	set t [::post::GetT];
	hwi OpenStack;
	
	hwi GetSessionHandle ss$t
	ss$t GetClientManagerHandle mg$t Animation
	mg$t GetRenderOptionsHandle op$t
	if { $flg == 1 } {
		set hyperViewColor(Background) [op$t GetBackgroundColor];
		set hyperViewColor(Foreground) [op$t GetForegroundColor];
		op$t SetBackgroundColor 1 1;
		op$t SetForegroundColor 0;
	} else {
		if { [ llength $hyperViewColor(Background) ] == 6 } {
			op$t SetBackgroundColor [ lrange $hyperViewColor(Background) 0 2 ] [ lrange $hyperViewColor(Background) 3 5 ];
		} elseif { [ llength $hyperViewColor(Background) ] == 3 } {
			op$t SetBackgroundColor $hyperViewColor(Background);
		} else {
			eval op$t SetBackgroundColor $hyperViewColor(Background);
		}
		if { [ llength $hyperViewColor(Foreground) ] == 3 } {
			op$t SetForegroundColor $hyperViewColor(Foreground);
		} else {
			eval op$t SetForegroundColor $hyperViewColor(Foreground);
		}
	}
	::post::Draw
	
	hwi CloseStack;
	return 0;
}

#####
proc ::hvCreDt::CtrDisp {{flg 0} args} {
	set t [::post::GetT];
	hwi OpenStack;
	
	set visflg [expr {$flg == 0 ? "false" : "true"}];
	
	# for Axis
	hwi GetSessionHandle s$t;
	s$t GetClientManagerHandle mn$t Animation;
	mn$t GetRenderOptionsHandle r$t;
	r$t SetGlobalAxisEnabled $visflg;
	
	# for Model info
	::post::GetPostHandle p$t;
	set mlist [p$t GetNoteList];
	foreach i $mlist {
		p$t GetNoteHandle n$t $i;
		if {[n$t GetLabel] == "Model Name"} {
			n$t SetVisibility $visflg;
		}
		n$t ReleaseHandle;
	}
	
	# for legend
	p$t SetDisplayOptions legend $visflg;
	
	::post::Draw;
	hwi CloseStack;
	return 0;
}

#####
proc ::hvCreDt::ExportH3D {filePath} {
	set t [::post::GetT];
	hwi OpenStack;
	::post::GetPostHandle p$t;

	::hvCreDt::explog 1 "Export h3d. <$filePath>";
	p$t ExportH3D $filePath;

	p$t ReleaseHandle;
	hwi CloseStack;
}

#####
proc ::hvCreDt::CreCapture {filePath} {
	set t [::post::GetT];
	hwi OpenStack;
	
	# 従来の方法だと、モデルの範囲が出力範囲になるので、Noteが見切れる場合がある
	#::post::GetPostHandle p$t;
	#p$t CaptureImageByRegion MODELSONLY "${fileN}.jpg" 1;

	hwi GetSessionHandle session$t
    session$t CaptureScreen jpg $filePath 100;
	
	hwi CloseStack;
	return 0;
}

#####
proc ::hvCreDt::CreateAnnotation {resultType analysisType} {
	variable annotationNotes;
	variable noteArea;

	if {![info exists annotationNotes]} {
		set annotationNotes [dict create];
		set noteArea [list]
	}

	::hvCreDt::CreateMinMaxNotes $resultType $analysisType;
	::hvCreDt::CreateNGNotes $resultType $analysisType;

	return 0;
}

#####
proc ::hvCreDt::CreateMinMaxNotes {resultType analysisType} {
	variable noteAttribute;

	set mfile "./temp/MaxMinVal.txt";
	if { ![file isfile $mfile]} {
		error 1;
	}

	set Max_DS_BDColor [dict get $noteAttribute "Max_DS_BorderColor"]
	set Max_DS_TextColor [dict get $noteAttribute "Max_DS_TextColor"]
	set Max_DS_BGColor [dict get $noteAttribute "Max_DS_BGColor"]
	set Max_DS_BDThickness [dict get $noteAttribute "Max_DS_BorderThickness"]
	set Max_DS_FontSize [dict get $noteAttribute "Max_DS_FontSize"]

	set Max_PL_BDColor [dict get $noteAttribute "Max_PL_BorderColor"]
	set Max_PL_TextColor [dict get $noteAttribute "Max_PL_TextColor"]
	set Max_PL_BGColor [dict get $noteAttribute "Max_PL_BGColor"]
	set Max_PL_BDThickness [dict get $noteAttribute "Max_PL_BorderThickness"]
	set Max_PL_FontSize [dict get $noteAttribute "Max_PL_FontSize"]

	set Min_DS_BDColor [dict get $noteAttribute "Min_DS_BorderColor"]
	set Min_DS_TextColor [dict get $noteAttribute "Min_DS_TextColor"]
	set Min_DS_BGColor [dict get $noteAttribute "Min_DS_BGColor"]
	set Min_DS_BDThickness [dict get $noteAttribute "Min_DS_BorderThickness"]
	set Min_DS_FontSize [dict get $noteAttribute "Min_DS_FontSize"]

	set Min_PL_BDColor [dict get $noteAttribute "Min_PL_BorderColor"]
	set Min_PL_TextColor [dict get $noteAttribute "Min_PL_TextColor"]
	set Min_PL_BGColor [dict get $noteAttribute "Min_PL_BGColor"]
	set Min_PL_BDThickness [dict get $noteAttribute "Min_PL_BorderThickness"]
	set Min_PL_FontSize [dict get $noteAttribute "Min_PL_FontSize"]

	set chid [open "${mfile}" r];
	while {! [eof $chid]} {
		set line [string trim [gets $chid]];
		set values [ split $line "," ];
		if { [llength $values] != 12 } {
			continue;
		}
		lassign $values aType rType DSMinNode DSMinVal DSMaxNode DSMaxVal \
			PLMinNode PLMinVal PLMaxNode PLMaxVal AverageDS AverageNotDS;
		if {$analysisType != $aType} {
			continue;
		}

		if {$resultType == "Thick value"} {
			# 0.01umで四捨五入
			set DSMaxValRound [::hvCreDt::Round $DSMaxVal 7];
			set PLMaxValRound [::hvCreDt::Round $PLMaxVal 7];

			# 最大(四捨五入)
			set DSMaxValInt [expr {int(round($DSMaxValRound * 1E6))}];
			set PLMaxValInt [expr {int(round($PLMaxValRound * 1E6))}];
			
			#puts "DSMax = $DSMaxVal -> $DSMaxValRound -> $DSMaxValInt"
			#puts "PLMax = $PLMaxVal -> $PLMaxValRound -> $PLMaxValInt"
			
			::hvCreDt::CreateNote $DSMaxNode $DSMaxValInt $Max_DS_BDColor $Max_DS_TextColor $Max_DS_BGColor $Max_DS_FontSize $Max_DS_BDThickness;
			::hvCreDt::CreateNote $PLMaxNode $PLMaxValInt $Max_PL_BDColor $Max_PL_TextColor $Max_PL_BGColor $Max_PL_FontSize $Max_PL_BDThickness;
		} else {
			# 0.01umで四捨五入
			set DSMinValRound [::hvCreDt::Round $DSMinVal 7];
			set PLMinValRound [::hvCreDt::Round $PLMinVal 7];

			# 最小(切り捨て)
			set DSMinValInt [expr {int(floor($DSMinValRound * 1E6))}];
			set PLMinValInt [expr {int(floor($PLMinValRound * 1E6))}];

			#puts "DSMin = $DSMinVal -> $DSMinValRound -> $DSMinValInt"
			#puts "PLMin = $PLMinVal -> $PLMinValRound -> $PLMinValInt"

			::hvCreDt::CreateNote $DSMinNode $DSMinValInt $Min_DS_BDColor $Min_DS_TextColor $Min_DS_BGColor $Min_DS_FontSize $Min_DS_BDThickness;
			::hvCreDt::CreateNote $PLMinNode $PLMinValInt $Min_PL_BDColor $Min_PL_TextColor $Min_PL_BGColor $Min_PL_FontSize $Min_PL_BDThickness;
		}
	}

	return 0;
}

proc ::hvCreDt::Round { value round } {
    set factor [ expr pow( 10, $round ) ];
    return [ expr round( $value * $factor ) / $factor ];
}

proc ::hvCreDt::CreateNGNotes {resultType analysisType} {
	variable noteAttribute;

	set mfile "./temp/NGVal.txt";
	if { ![file isfile $mfile]} {
		error 1;
	}

	set Max_NG_DS_BorderColor [dict get $noteAttribute "Max_NG_DS_BorderColor"];
	set Max_NG_DS_TextColor [dict get $noteAttribute "Max_NG_DS_TextColor"];
	set Max_NG_DS_BGColor [dict get $noteAttribute "Max_NG_DS_BGColor"];
	set Max_NG_DS_BorderThickness [dict get $noteAttribute "Max_NG_DS_BorderThickness"];
	set Max_NG_DS_FontSize [dict get $noteAttribute "Max_NG_DS_FontSize"];

	set Max_NG_PL_BorderColor [dict get $noteAttribute "Max_NG_PL_BorderColor"];
	set Max_NG_PL_TextColor [dict get $noteAttribute "Max_NG_PL_TextColor"];
	set Max_NG_PL_BGColor [dict get $noteAttribute "Max_NG_PL_BGColor"];
	set Max_NG_PL_BorderThickness [dict get $noteAttribute "Max_NG_PL_BorderThickness"];
	set Max_NG_PL_FontSize [dict get $noteAttribute "Max_NG_PL_FontSize"];

	set Min_NG_DS_BorderColor [dict get $noteAttribute "Min_NG_DS_BorderColor"];
	set Min_NG_DS_TextColor [dict get $noteAttribute "Min_NG_DS_TextColor"];
	set Min_NG_DS_BGColor [dict get $noteAttribute "Min_NG_DS_BGColor"];
	set Min_NG_DS_BorderThickness [dict get $noteAttribute "Min_NG_DS_BorderThickness"];
	set Min_NG_DS_FontSize [dict get $noteAttribute "Min_NG_DS_FontSize"];

	set Min_NG_PL_BorderColor [dict get $noteAttribute "Min_NG_PL_BorderColor"];
	set Min_NG_PL_TextColor [dict get $noteAttribute "Min_NG_PL_TextColor"];
	set Min_NG_PL_BGColor [dict get $noteAttribute "Min_NG_PL_BGColor"];
	set Min_NG_PL_BorderThickness [dict get $noteAttribute "Min_NG_PL_BorderThickness"];
	set Min_NG_PL_FontSize [dict get $noteAttribute "Min_NG_PL_FontSize"];

	set chid [open "${mfile}" r];
	while {! [eof $chid]} {
		set line [string trim [gets $chid]];
		set values [ split $line "," ];
		if { [llength $values] != 6 } {
			continue;
		}
		lassign $values aType nType rType area nodeID value;
		if {$analysisType != $aType || $resultType != $rType } {
			continue;
		}

		# 0.01umで四捨五入
		set valueRound [::hvCreDt::Round $value 7];

		if {$resultType == "Thick value"} {
			# 過剰（四捨五入）
			set valueInt [expr {int(round($valueRound * 1E6))}];
			if {$nType == "DS"} {
				set bdColor $Max_NG_DS_BorderColor;
				set textColor $Max_NG_DS_TextColor;
				set bgColor $Max_NG_DS_BGColor;
				set bdThickness $Max_NG_DS_BorderThickness;
				set fontSize $Max_NG_DS_FontSize;
			} else {
				set bdColor $Max_NG_PL_BorderColor;
				set textColor $Max_NG_PL_TextColor;
				set bgColor $Max_NG_PL_BGColor;
				set bdThickness $Max_NG_PL_BorderThickness;
				set fontSize $Max_NG_PL_FontSize;
			}
			#puts "Ext = $value -> $valueRound -> $valueInt"
		} else {
			# 不足（切り捨て）
			set valueInt [expr {int(floor($valueRound * 1E6))}];
			if {$nType == "DS"} {
				set bdColor $Min_NG_DS_BorderColor;
				set textColor $Min_NG_DS_TextColor;
				set bgColor $Min_NG_DS_BGColor;
				set bdThickness $Min_NG_DS_BorderThickness;
				set fontSize $Min_NG_DS_FontSize;
			} else {
				set bdColor $Min_NG_PL_BorderColor;
				set textColor $Min_NG_PL_TextColor;
				set bgColor $Min_NG_PL_BGColor;
				set bdThickness $Min_NG_PL_BorderThickness;
				set fontSize $Min_NG_PL_FontSize;
			}
			#puts "Short = $value -> $valueRound -> $valueInt"
		}

		::hvCreDt::CreateNote $nodeID $valueInt $bdColor $textColor $bgColor $fontSize $bdThickness;
	}
	return 0;
}

proc ::hvCreDt::CreateNote {nodeID value {bdColor "0 0 0"} {textColor "0 0 0"} {bgColor "255 255 255"} {size 10} {border 2}} {
	variable annotationNotes;

	hwi OpenStack;

    set t [ ::post::GetT ]
	::post::GetPostHandle post$t;

	# create new note
    set noteID [ post$t AddNote ];
    post$t GetNoteHandle note$t $noteID;
	dict lappend annotationNotes $nodeID $noteID;

	# set attribute of note(font)
    set modelID [ post$t GetActiveModel ]
    note$t SetAttachment "node $modelID $nodeID"
    note$t SetText "$value"
    note$t SetPositionToAttachment true
    note$t SetScreenAnchor false
    note$t SetBorderThickness $border
    note$t GetFontHandle font$t $noteID
    note$t SetColor $bdColor
    note$t SetTextColor $textColor
	note$t SetBackgroundColor $bgColor
    note$t SetVisibility true
    note$t SetTransparency false
    font$t SetWeight normal
    font$t SetFamily Arial
    font$t SetSize $size
    post$t Draw

    # SetPositionToAttachment=true の場合、左端が節点位置
    set textArea [ note$t GetBoundingBox ]
    lassign $textArea minX minY maxX maxY
    set nodeArea [ list $minX $minY $minX $minY ]

    # テキストエリアがかぶっていないか確認（接点位置を登録する前にチェックするのは、自身の節点範囲との交差を見ないようにするため）
    set isValid [ ::hvCreDt::IsValidArea note$t ]

    # 節点位置をかぶっていはいけない禁止エリアに登録する
    ::hvCreDt::RegistrProhibitedArea $nodeArea

    # テキストエリアがかぶっていないか確認
    if { !$isValid } {
        ::hvCreDt::MovePosition note$t post$t
    }

    # テキストエリアを禁止エリアに登録する
    set textArea [ note$t GetBoundingBox ]
    ::hvCreDt::RegistrProhibitedArea $textArea

	hwi CloseStack;

	return 0;
}

#####
proc ::hvCreDt::IsValidArea { note } {
    if { [ IsOuter $note ] } { return false }
    if { [ IsIntersected $note ] } { return false }
    return true
}

#####
proc ::hvCreDt::IsIntersected { note } {
	variable noteArea;

    if { [ llength $noteArea ] == 0 } {
        return false
    }

    set area1 [ $note GetBoundingBox ]
    foreach area2 $noteArea {
        if { [ IsIntersectedArea $area1 $area2 ] } {
            return true
        }
    }
    return false
}

#####
proc ::hvCreDt::IsIntersectedArea { area1 area2 } {
    lassign $area1 minX1 minY1 maxX1 maxY1
    lassign $area2 minX2 minY2 maxX2 maxY2
    if { $minX1 > $maxX2 } { return false }
    if { $maxX1 < $minX2 } { return false }
    if { $minY1 > $maxY2 } { return false }
    if { $maxY1 < $minY2 } { return false }
    return true
}

#####
proc ::hvCreDt::IsOuter { note } {
	variable pageHeight;
	variable pageWidht;

    set area [ $note GetBoundingBox ]
    lassign $area minX1 minY1 maxX1 maxY1
    if { $minX1 < 0 } { return true }
    if { $minY1 < 0 } { return true }
    if { $maxX1 > $pageWidht } { return true }
    if { $maxY1 > $pageHeight } { return true }
    return false
}

#####
proc ::hvCreDt::RegistrProhibitedArea { area } {
	variable noteArea;
    lappend noteArea $area
}

#####
proc ::hvCreDt::MovePosition {note post} {
	variable pageHeight;
	variable pageWidht;

    set area [ $note GetBoundingBox ]
    lassign $area minX minY maxX maxY
    set width [ expr { $maxX - $minX } ]
    set height [ expr { $maxY - $minY } ]
    set step [ expr { int([ ::hvCreDt::Length [ list $minX $minY ] [ list $maxX $maxY ] ]) } ]
    set step [ expr { max($step, 5) } ]

    set min [ list $minX $minY ]
    set max [ list $maxX $maxY ]
    set p1 [ list 0 0 ]
    set p2 [ list 0 $pageHeight ]
    set p3 [ list $pageWidht 0 ]
    set p4 [ list $pageWidht $pageHeight ]

    set d1 [ Length $min $p1 ]
    set d2 [ Length $min $p2 ]
    set d3 [ Length $min $p3 ]
    set d4 [ Length $min $p4 ]
    set maxD [ expr { max(max($d1,$d2), max($d3,$d4))} ]

    set pi [ expr { acos(-1) } ]
    set rmin 0
    set maxCount 20
    $note SetPositionToAttachment false
    while { $rmin < $maxD } {
        set iCount 0
        while { $iCount < $maxCount } {
            incr iCount
            set r [ expr { $rmin + $step * rand() } ]
            set theta [ expr {2.0 * $pi * rand() } ]
            set x1 [ expr { int($minX + $r * cos($theta)) } ]
            set y1 [ expr { int($minY + $r * sin($theta)) } ]
            set px [ expr double($x1) / $pageWidht ]
            set py [ expr 1.0 - double($y1) / $pageHeight ]
            if { [ $note SetPosition $px $py ] != 0 } {
                continue
            }

            $post Draw
            if { [ ::hvCreDt::IsValidArea $note ] } {
                return
            }
        }
        incr rmin $step
    }    

    $note SetPositionToAttachment true
    return 
}

#####
proc ::hvCreDt::Length { xy1 xy2 } {
    lassign $xy1 x1 y1
    lassign $xy2 x2 y2
    set d [ expr { ($x2 - $x1)**2 + ($y2 - $y1)**2 } ]
    if { $d < 0.0 } {
        return 0.0
    }
    return [ expr { sqrt($d) } ]
}

#####
proc ::hvCreDt::MoveAnnotationToNode {args} {
	variable annotationNotes;

	hwi OpenStack;
    set t [ ::post::GetT ]
	::post::GetPostHandle post$t;

	dict for {nodeID noteList} $annotationNotes {
		# 重複は節点にアタッチさせると被るので戻さない
		if {[llength $noteList] >= 2} {
			::hvCreDt::explog 1 "Do not attach duplicates to contacts. nodeID=$nodeID, noteList=$noteList";
			continue;
		}
		set noteID [lindex $noteList 0];
		post$t GetNoteHandle note$t $noteID;
		note$t SetPositionToAttachment true;
		note$t ReleaseHandle;
	}

	post$t Draw;
	hwi CloseStack;

	return 0;
}

#####
proc ::hvCreDt::DeleteAnnotation {args} {
	variable annotationNotes;
	variable noteArea;

	hwi OpenStack;
    set t [ ::post::GetT ]
	::post::GetPostHandle post$t;

	dict for {nodeID noteList} $annotationNotes {
		foreach noteID $noteList {
			post$t RemoveNote $noteID;
		}
	}
	set annotationNotes [dict create];
	set noteArea [list]

	post$t Draw;
	hwi CloseStack;

	return 0;
}

#####
proc ::hvCreDt::explog {{flg 0} {msgD ""} {err 0} args} {
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
proc ::hvCreDt::errfile {args} {
	set fileN  "./Errorflg"
	set chid [open "${fileN}" w];
	close $chid;
	return 0;
}

::hvCreDt::main;
