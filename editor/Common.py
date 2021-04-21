BS = 32

APP_NAME = 'RouteMaster'

# these svg files cannot be rendered properly by Qt
PNG_POLYFILLS = set(filter(lambda x: x.strip(), """
BSicon_BLaq.svg
BSicon_LKRWl.svg
BSicon_uLKRW%2Br.svg
BSicon_KBL4.svg
BSicon_lhvCONTg(l)q.svg
BSicon_uexkLLSTR%2B4.svg
BSicon_LLSTRr%2B1.svg
BSicon_uexLSTR.svg
BSicon_uexhLSTRr.svg
BSicon_WALKl.svg
BSicon_uexkLLSTR3.svg
BSicon_exkLLSTRc3.svg
BSicon_uexhkLLSTRc2.svg
BSicon_uhLSTR.svg
BSicon_exLSTR.svg
BSicon_GRZ3%2B4.svg
BSicon_HUBtr-4.svg
BSicon_HUBrf-L.svg
BSicon_hkLLSTR3%2Bl.svg
BSicon_HUBlg-L.svg
BSicon_lHUB.svg
BSicon_GRZ2%2B1.svg
BSicon_4HUBe@G.svg
BSicon_lENDE@F.svg
BSicon_uexLSTR2%2Br.svg
BSicon_4HUBe@F.svg
BSicon_lENDE@G.svg
BSicon_dMHUB.svg
BSicon_4HUBa@Lq.svg
BSicon_4HUBa@G~FFq.svg
BSicon_uexhkLLSTRr%2B1.svg
BSicon_uhLSTR%2Br.svg
BSicon_uLKRWg%2Br.svg
BSicon_uexhkLLSTRc3.svg
BSicon_exkLLSTRc2.svg
BSicon_uexkLLSTR2.svg
BSicon_4HUBe@F~GG.svg
BSicon_kLLSTRr%2B1.svg
BSicon_GRZaq.svg
BSicon_exLLSTR3%2B1a.svg
BSicon_exLKRWg%2Br.svg
BSicon_HUBs%2Bl-R.svg
BSicon_HUBxaq.svg
BSicon_uexkLLSTRl%2B4.svg
BSicon_HUBe@g-L.svg
BSicon_hLKRW%2Bl.svg
BSicon_uexLSTRl.svg
BSicon_BLl%2B4.svg
BSicon_GRZTr.svg
BSicon_uexLKRW%2Bl.svg
BSicon_HUBlf.svg
BSicon_GRZTe.svg
BSicon_cHUBlf-L.svg
BSicon_exLSTR%2Bl.svg
BSicon_uexhLSTRq.svg
BSicon_cHUBrg-L.svg
BSicon_kLLSTR3%2Bl.svg
BSicon_lv-ENDE@F.svg
BSicon_LSTR.svg
BSicon_v-LSHI2%2Bl.svg
BSicon_uexhkLLSTRc1.svg
BSicon_gLLSTR2.svg
BSicon_uLLSTR2%2B4a.svg
BSicon_4HUBe@Rq.svg
BSicon_gLSTR%2Br.svg
BSicon_ukLLSTR%2B4.svg
BSicon_uexhkLLSTR3%2Bl.svg
BSicon_GRZ2%2Br.svg
BSicon_4HUBe@R.svg
BSicon_hkLLSTRr%2B1.svg
BSicon_gLLSTR3.svg
BSicon_4HUBe@Gq.svg
BSicon_exkLLSTRc1.svg
BSicon_exkLLSTR%2B1.svg
BSicon_%2Bc.svg
BSicon_lv-ENDE@G.svg
BSicon_exhkLLSTR2%2Br.svg
BSicon_uexLKRWg%2Bl.svg
BSicon_PFERD.svg
BSicon_GRZar.svg
BSicon_LLSTR3%2Bl.svg
BSicon_uexhLSTR%2Bl.svg
BSicon_GRZf%2Bl.svg
BSicon_HUBx-L.svg
BSicon_uexLLSTR3%2B1e.svg
BSicon_fexLKRW%2Br.svg
BSicon_HUBlg.svg
BSicon_KBL2.svg
BSicon_BLl%2Bg.svg
Stadium_-_The_Noun_Project.svg
BSicon_hLKRWr.svg
BSicon_dHUB-Rq.svg
BSicon_uexLLSTR3%2B1a.svg
BSicon_ukLLSTR3.svg
BSicon_uLSTR3%2Bl.svg
BSicon_fexLSTR.svg
BSicon_exkLLSTRl%2B4.svg
BSicon_uLSTR3.svg
BSicon_uLSTRr.svg
BSicon_HUBtr.svg
BSicon_4HUBa@R.svg
BSicon_uexhkLLSTRc4.svg
BSicon_fLKRWl.svg
BSicon_exLSTR3%2Bl.svg
BSicon_exl-ENDE@Fq.svg
BSicon_LKRW%2Br.svg
BSicon_4HUBe@Fq.svg
BSicon_ukLLSTR%2B1.svg
BSicon_uhLKRWr.svg
BSicon_dHUBq.svg
BSicon_cdGRZq.svg
BSicon_uexLSTR2%2B4.svg
BSicon_exLLSTR1%2B4.svg
BSicon_HUBsr-L.svg
BSicon_uLLSTR2%2B4e.svg
BSicon_HUBtr-3.svg
BSicon_uexLSTR3%2B1.svg
BSicon_HUB1%2B2.svg
BSicon_exkLLSTRc4.svg
BSicon_exkLLSTR%2B4.svg
BSicon_HUB-L.svg
BSicon_uLSTR2.svg
BSicon_fLKRW%2Br.svg
BSicon_ukLLSTR2.svg
BSicon_uhkLLSTR3%2Bl.svg
BSicon_dHUBa@f-Lq.svg
BSicon_GRZTa.svg
BSicon_KBL3.svg
BSicon_uhkLLSTRr%2B1.svg
BSicon_KBL1.svg
BSicon_ukLLSTR2%2Br.svg
BSicon_HUBtf.svg
BSicon_uLSTRq.svg
BSicon_uexkLLSTR%2B1.svg
BSicon_numN000.svg
BSicon_4HUBa@F.svg
BSicon_lhvCONTf(l)q.svg
BSicon_exLLSTR3%2B1e.svg
BSicon_%2Bd.svg
BSicon_exv-LSHI2r.svg
BSicon_4HUBe@R~LLq.svg
BSicon_GRZ3%2B1.svg
BSicon_dHUBeq.svg
BSicon_exLKRWr.svg
BSicon_uexvLSHI2l-.svg
BSicon_GRZ2%2B4.svg
BSicon_MINE.svg
BSicon_exhLSTRq.svg
BSicon_uexhkLLSTR3.svg
BSicon_-GRZq.svg
BSicon_uexhkLLSTR2.svg
BSicon_LKRWgr.svg
BSicon_dHUBrf-L.svg
BSicon_dHUBlg-L.svg
BSicon_exLSTRr%2B1.svg
BSicon_uexhv-LSHI2r.svg
BSicon_LSTRl%2B4.svg
BSicon_4HUBa@G.svg
BSicon_lGIP.svg
BSicon_lhvCONTf(r).svg
BSicon_uLSTRr%2B1.svg
BSicon_HUBtg.svg
BSicon_HUBaq.svg
BSicon_uLKRWgr.svg
BSicon_kLLSTR2.svg
BSicon_BL.svg
BSicon_uLLSTR3%2B1.svg
BSicon_uLSTR%2Bl.svg
BSicon_exkLLSTR3.svg
BSicon_HUB1f.svg
BSicon_fexLKRWr.svg
BSicon_uLLSTR2%2B4.svg
BSicon_cGRZq.svg
BSicon_4HUBe@L~RR.svg
BSicon_GRZel.svg
BSicon_HUBsc1.svg
BSicon_v-LSHI2r.svg
BSicon_LSTR2.svg
BSicon_BICYCLE.svg
BSicon_LLSTRl%2B4.svg
BSicon_HUBsl-L.svg
BSicon_kLLSTRl%2B4.svg
BSicon_HUBtl-2.svg
BSicon_4HUBa@Fq.svg
BSicon_%2Bcd.svg
BSicon_uexhLKRWl.svg
BSicon_uLABZl%2Bl.svg
BSicon_ukLLSTRc1.svg
BSicon_uhkLLSTR%2B1.svg
BSicon_LABZqr.svg
BSicon_GRZq.svg
BSicon_uhLKRW%2Bl.svg
BSicon_BLX.svg
BSicon_GRZ.svg
BSicon_uexkLLSTRr%2B1.svg
BSicon_BL3%2Bl.svg
BSicon_LSTR3.svg
BSicon_LSTRr.svg
BSicon_HUBx-24.svg
BSicon_GRZ14.svg
BSicon_gLLSTR2%2Br.svg
BSicon_uexhkLLSTRl%2B4.svg
BSicon_exLLSTR3%2B4.svg
BSicon_exhLKRW%2Bl.svg
BSicon_HUBsr.svg
BSicon_LKRWg%2Br.svg
BSicon_uexLLSTR%2B1.svg
BSicon_exkLLSTR2.svg
BSicon_uLSTR.svg
BSicon_lhvCONTf(l).svg
BSicon_uexLSTR%2B1.svg
BSicon_exLLSTR2%2B1.svg
BSicon_kLLSTR3.svg
BSicon_BL%2B4.svg
BSicon_uexLSTR%2Br.svg
BSicon_HUBlf-L.svg
BSicon_exLLSTR2%2B3.svg
BSicon_exLLSTR2%2Br.svg
BSicon_HUBrg-L.svg
BSicon_uexLKRWgl.svg
BSicon_FLUG.svg
BSicon_HUBa@f-R.svg
BSicon_exLKRW%2Br.svg
BSicon_HUB%2Bl.svg
BSicon_HUBsc2.svg
BSicon_dHUB-Lq.svg
BSicon_BLr%2Bg.svg
BSicon_uexkLLSTR3%2Bl.svg
BSicon_dGRZ.svg
BSicon_uexLLSTR3%2B1.svg
BSicon_BLr%2B1.svg
BSicon_GRZ2.svg
Northern_line_roundel_(no_text).svg
BSicon_uexLLSTR2%2B4.svg
BSicon_ukLLSTRc3.svg
BSicon_lcdHUB.svg
BSicon_exHUBeq.svg
BSicon_HUB%2Bl-R.svg
BSicon_l-ENDE@Gq.svg
BSicon_HUBtl-1.svg
BSicon_ukLLSTRc2.svg
BSicon_LLSTR3%2B1e.svg
BSicon_BLl.svg
BSicon_GRZe.svg
BSicon_GRZr.svg
BSicon_GRZ3.svg
BSicon_KGRZ4.svg
BSicon_LSTRq.svg
BSicon_uexLKRWr.svg
BSicon_HUB2%2B4.svg
BSicon_HUBsc3.svg
BSicon_4HUBe@L~RRq.svg
BSicon_kLLSTRc4.svg
BSicon_xLABZqr.svg
BSicon_hkLLSTRl%2B4.svg
BSicon_lhvCONTf(r)q.svg
BSicon_uexhLKRW%2Br.svg
BSicon_dHUBa@f-Rq.svg
BSicon_ENDE%2Brxe.svg
BSicon_HUB3%2Bg.svg
BSicon_HUB3%2B1.svg
BSicon_uLABZqlr.svg
BSicon_lhLSTR.svg
BSicon_HUBs%2Br-R.svg
BSicon_BL%2B1.svg
BSicon_gLLSTR3%2B1.svg
BSicon_BUS2.svg
BSicon_HUBrf.svg
BSicon_gLLSTR2%2B4.svg
BSicon_HUBl.svg
BSicon_uLABZq%2Blr.svg
BSicon_4HUBe@Lq.svg
BSicon_GRZa.svg
BSicon_LSTR%2Bl.svg
BSicon_uv-LSHI2r.svg
BSicon_exkLLSTRr%2B1.svg
BSicon_LLSTR3%2B1a.svg
BSicon_CHURCH.svg
BSicon_LSTR3%2Bl.svg
BSicon_l-ENDE@Fq.svg
BSicon_numEl.svg
BSicon_uLKRWl.svg
BSicon_HUBl-R.svg
BSicon_lGIPl.svg
BSicon_cREq.svg
BSicon_lGIPlq.svg
BSicon_BUILDING.svg
BSicon_cdHUBaq.svg
BSicon_KGRZ1.svg
BSicon_BUILDINGr.svg
BSicon_exhLKRWl.svg
BSicon_kLLSTRc1.svg
BSicon_HUB2%2Bg.svg
BSicon_HUBc12.svg
BSicon_uhLSTRl.svg
BSicon_uLLSTR2%2Br.svg
BSicon_HUBrg.svg
BSicon_hLSTR.svg
BSicon_BUS3.svg
BSicon_HUB3%2B4.svg
BSicon_gLSTRr.svg
BSicon_WPump.svg
BSicon_lhvCONTg(r)q.svg
BSicon_GRZq-.svg
BSicon_uLLSTR2.svg
BSicon_HUB.svg
BSicon_HUBs%2Bl.svg
BSicon_HUBx.svg
BSicon_HUBsc4.svg
BSicon_kLLSTRc3.svg
BSicon_GRZ%2Bl.svg
BSicon_KGRZ3.svg
BSicon_exLKRWgl.svg
BSicon_4HUBa@G~FF.svg
BSicon_uhkLLSTRl%2B4.svg
BSicon_4HUBa@R~LL.svg
BSicon_VIEWl.svg
BSicon_LLSTR2.svg
BSicon_4HUBa@Gq.svg
BSicon_LSTRr%2B1.svg
BSicon_exkLLSTR3%2Bl.svg
BSicon_uexLLSTR2%2Br.svg
BSicon_uhkLLSTR%2B4.svg
BSicon_uLSTRl%2B4.svg
BSicon_ukLLSTRc4.svg
BSicon_LLSTR3.svg
BSicon_4HUBa@Rq.svg
BSicon_GNDC.svg
BSicon_KGRZ2.svg
BSicon_kLLSTRc2.svg
BSicon_BLf%2Br.svg
BSicon_exLLSTR3%2B1.svg
BSicon_exLSTRl.svg
BSicon_uLLSTR3.svg
BSicon_fLSTRq.svg
BSicon_gLSTRq.svg
BSicon_exLSTRl%2B4.svg
BSicon_uexLLSTR%2B4.svg
BSicon_BL%2Br.svg
BSicon_uexLSTR%2B4.svg
BSicon_exLLSTR2%2B4.svg
BSicon_FLUGg.svg
BSicon_uLLSTRr%2B1.svg
BSicon_w.svg
BSicon_lHUB%2Bd.svg
BSicon_HORSECAR.svg
BSicon_uLSTR%2Br.svg
BSicon_uexLLSTR2%2B4a.svg
BSicon_GRZl%2Bg.svg
BSicon_HUBe@g-Lq.svg
BSicon_fexLKRWl.svg
BSicon_v-LSHI2l.svg
BSicon_GRZer.svg
BSicon_lNULf.svg
BSicon_dBLe.svg
BSicon_kHUBe@Fq.svg
BSicon_hkLLSTRc1.svg
BSicon_lvENDE@F-.svg
BSicon_lvENDE@G.svg
BSicon_GRZ4m1.svg
BSicon_uexkLLSTRc3.svg
BSicon_HUBsl-R.svg
BSicon_BUS.svg
BSicon_uexkLLSTRc2.svg
BSicon_uexhLKRWr.svg
BSicon_HUBa@fq.svg
BSicon_lvENDE@F.svg
BSicon_uLLSTR3%2B1e.svg
BSicon_BLq.svg
BSicon_GRZx.svg
BSicon_LSTR%2B4.svg
BSicon_uhLKRW%2Br.svg
BSicon_exkLLSTR2%2Br.svg
BSicon_uexLLSTR3%2Bl.svg
BSicon_LSTRl.svg
BSicon_HUB4.svg
BSicon_TRAM.svg
BSicon_exhLKRW%2Br.svg
BSicon_FACTORY.svg
BSicon_HUBsl.svg
BSicon_LKRWg%2Bl.svg
BSicon_HUB3f.svg
BSicon_HUB-Rq.svg
BSicon_FLUGf.svg
BSicon_bs.svg
BSicon_c.svg
BSicon_HUBrg-R.svg
BSicon_HUBlf-R.svg
BSicon_uexLSTR%2Bl.svg
BSicon_HUBxeq.svg
BSicon_uexLKRWgr.svg
BSicon_lENDE@Gq.svg
BSicon_HUBa@f-L.svg
BSicon_WORKS.svg
BSicon_exLKRW%2Bl.svg
BSicon_HUBtf-2.svg
BSicon_GRZeq.svg
BSicon_exLLSTR2%2B4e.svg
BSicon_HUB%2Br.svg
BSicon_GRZ23.svg
BSicon_cMHUB.svg
BSicon_BL3%2B1.svg
BSicon_HUBx-13.svg
BSicon_uexLLSTRr%2B1.svg
BSicon_dBLq.svg
BSicon_cGRZ.svg
BSicon_kLLSTR%2B4.svg
BSicon_LSTR2%2Br.svg
BSicon_exldENDE@Gq.svg
BSicon_BL2.svg
BSicon_BL2%2B4.svg
BSicon_hkLLSTRc2.svg
BSicon_vGRZ-.svg
BSicon_4HUBa@R~LLq.svg
BSicon_HANDCAR.svg
BSicon_LLSTR1%2B4.svg
BSicon_ukLLSTRl%2B4.svg
BSicon_uexkLLSTRc1.svg
BSicon_hkLLSTRc3.svg
BSicon_HUBf%2B4.svg
BSicon_uLLSTR%2B1.svg
BSicon_hkLLSTR%2B1.svg
BSicon_BLr.svg
BSicon_BL3.svg
BSicon_GRZl.svg
BSicon_BLe.svg
BSicon_exhLSTR.svg
BSicon_uexLKRWl.svg
BSicon_HUBa.svg
BSicon_MHUB.svg
BSicon_GRZ%2B4.svg
BSicon_HUBtf-3.svg
BSicon_uexhLKRW%2Bl.svg
BSicon_exLLSTR%2B1.svg
BSicon_uLLSTR3%2Bl.svg
BSicon_uLSTR%2B1.svg
BSicon_FLUGr.svg
BSicon_fexLSTR%2Br.svg
BSicon_BLeq.svg
BSicon_b.svg
BSicon_lv-ENDE.svg
BSicon_FIGHTER.svg
BSicon_HUBs%2Br-L.svg
BSicon_gLLSTRr%2B1.svg
BSicon_HUBeq.svg
BSicon_dBL.svg
BSicon_exLLSTR3%2Bl.svg
BSicon_cdREq.svg
BSicon_exHUBq.svg
BSicon_HUBe.svg
BSicon_HUBr.svg
BSicon_HUB3.svg
BSicon_kLLSTR%2B1.svg
BSicon_REST.svg
BSicon_lENDE@Gq-.svg
BSicon_BOOT.svg
BSicon_BLa.svg
BSicon_LSTR%2Br.svg
BSicon_4HUBe@R~LL.svg
BSicon_uLABZ%2Blr.svg
BSicon_VIEWf.svg
BSicon_uexkLLSTR2%2Br.svg
BSicon_lhvCONTg(r).svg
BSicon_HUBx-Rq.svg
BSicon_lvENDE-.svg
BSicon_uLLSTR%2B4.svg
BSicon_HUBf%2B1.svg
BSicon_hkLLSTR%2B4.svg
BSicon_uLKRWr.svg
BSicon_VIEWg.svg
BSicon_ELC-S2.svg
BSicon_uexkLLSTRc4.svg
BSicon_dHUBtg.svg
BSicon_dHUBaq.svg
BSicon_lGIPr.svg
BSicon_dREq.svg
BSicon_BUILDINGl.svg
BSicon_GRZ%2B1.svg
BSicon_exhLKRWr.svg
BSicon_exLLSTR2%2B4a.svg
BSicon_HUB2.svg
BSicon_lENDE@Fq.svg
BSicon_uhLSTRr.svg
BSicon_fLSTR%2Br.svg
BSicon_exLSTRq.svg
BSicon_exLLSTR%2B4.svg
BSicon_uexLSTRl%2B4.svg
BSicon_gLSTRl.svg
BSicon_uLSTR%2B4.svg
BSicon_vLSHI2%2Br-.svg
BSicon_lHUB%2Bc.svg
BSicon_cd.svg
BSicon_vLSHI2r-.svg
BSicon_GRZl%2B4.svg
BSicon_GENAIR.svg
BSicon_HUB2f.svg
BSicon_exLSTR2.svg
BSicon_HUBs%2Br.svg
BSicon_GRZ%2Br.svg
BSicon_HUBq.svg
BSicon_exLKRWgr.svg
BSicon_REq.svg
BSicon_exvLSHI2l-.svg
BSicon_exhkLLSTRl%2B4.svg
BSicon_exhkLLSTR3.svg
BSicon_uexv-LSHI2r.svg
BSicon_dHUBa@fq.svg
BSicon_VIEWr.svg
BSicon_uLLSTR3%2B1a.svg
BSicon_hkLLSTRc4.svg
BSicon_LSTR3%2B1.svg
BSicon_BL2%2Br.svg
BSicon_ANCHOR330.svg
BSicon_lvENDE@G-.svg
BSicon_ELC-S1.svg
BSicon_LSTR2%2B4.svg
BSicon_LSTR%2B1.svg
BSicon_exhkLLSTR2.svg
BSicon_TRAM1.svg
BSicon_.svg
BSicon_kHUBe@Gq.svg
BSicon_hLSTRq.svg
BSicon_dBLa.svg
BSicon_cHUBq.svg
BSicon_HUBa@f-Rq.svg
BSicon_HUB1.svg
BSicon_BLf%2Bl.svg
BSicon_SHOPPING.svg
BSicon_uhLSTRq.svg
BSicon_exLLSTRr%2B1.svg
BSicon_exLSTR3.svg
BSicon_exLSTRr.svg
BSicon_gLLSTR3%2Bl.svg
BSicon_uexLLSTR2%2B4e.svg
BSicon_d.svg
BSicon_BL%2Bl.svg
BSicon_GRZ2m3.svg
BSicon_s.svg
BSicon_BLc1.svg
BSicon_LKRWr.svg
BSicon_uexLSTRq.svg
BSicon_LLSTR2%2B4.svg
BSicon_uLKRW%2Bl.svg
BSicon_HUBx-1.svg
BSicon_LLSTR3%2B1.svg
BSicon_hkLLSTR3.svg
BSicon_uexhLSTRl.svg
BSicon_exhkLLSTR%2B4.svg
BSicon_uhkLLSTRc1.svg
BSicon_ukLLSTR3%2Bl.svg
BSicon_vLSHI2l-.svg
BSicon_exhkLLSTRc1.svg
BSicon_uLLSTRl%2B4.svg
BSicon_exlvENDE@F-.svg
BSicon_lENDE1.svg
BSicon_kHUBe@G.svg
BSicon_LENDEg.svg
BSicon_LLSTR2%2B4a.svg
BSicon_gLLSTR%2B4.svg
BSicon_HUBlg-R.svg
BSicon_HUBrf-R.svg
BSicon_GRZ3m4.svg
BSicon_HUBa@f.svg
BSicon_HUBr-L.svg
BSicon_exHUBaq.svg
BSicon_cHUBaq.svg
BSicon_HUBa@f-Lq.svg
BSicon_REPAIR.svg
BSicon_kHUBe@F.svg
BSicon_LENDEf.svg
BSicon_hkLLSTR-c1.svg
BSicon_uhLSTR%2Bl.svg
BSicon_lENDEq.svg
BSicon_uLKRWg%2Bl.svg
BSicon_ldENDE.svg
BSicon_exLKRWg%2Bl.svg
BSicon_hkLLSTR2.svg
BSicon_exLSTR%2B1.svg
BSicon_HUBs%2Bl-L.svg
BSicon_dGRZe.svg
BSicon_HUBc4.svg
BSicon_lDAMPF.svg
BSicon_uLABZlr.svg
BSicon_HUBe@g-R.svg
BSicon_hLKRW%2Br.svg
BSicon_uLSTR2%2Br.svg
BSicon_GRZTl.svg
BSicon_uexLSTR3.svg
BSicon_uexLSTRr.svg
BSicon_BLc2.svg
BSicon_uexLLSTRl%2B4.svg
BSicon_uexLKRW%2Br.svg
BSicon_cdHUBq.svg
BSicon_uexLLSTR3.svg
BSicon_LRP2.svg
BSicon_HUBx-2.svg
BSicon_exLSTR%2Br.svg
BSicon_uhkLLSTRc2.svg
BSicon_lhvCONTg(l).svg
BSicon_HUBtg-1.svg
BSicon_exhkLLSTRc2.svg
BSicon_lENDE2.svg
BSicon_HUBx-Lq.svg
BSicon_hkLLSTR-c3.svg
BSicon_gLSTR%2Bl.svg
BSicon_ldENDE@Gq.svg
BSicon_exLSTR2%2Br.svg
BSicon_gLSTR.svg
BSicon_kHUBa@Gq.svg
BSicon_udLSTR2.svg
BSicon_4HUBe@L.svg
BSicon_hkLLSTR-c2.svg
BSicon_fexLSTRq.svg
BSicon_lENDE3.svg
BSicon_cHUB-L.svg
BSicon_dHUBtg-4.svg
BSicon_exhkLLSTRc3.svg
BSicon_HUBe@gq.svg
BSicon_ukLLSTRr%2B1.svg
BSicon_lvNULgfq.svg
BSicon_uhkLLSTRc3.svg
BSicon_GRZal.svg
BSicon_LLSTR%2B1.svg
BSicon_uexLKRWg%2Br.svg
BSicon_uexhLSTR%2Br.svg
BSicon_GRZf%2Br.svg
BSicon_HUBx-3.svg
BSicon_HUBx-R.svg
BSicon_uhkLLSTR2%2Br.svg
BSicon_WindPump.svg
BSicon_uexLLSTR2.svg
BSicon_dGRZq.svg
BSicon_ldHUB.svg
BSicon_uexhkLLSTR%2B1.svg
BSicon_lENDE.svg
BSicon_fexLKRW%2Bl.svg
BSicon_uexLSTR2.svg
BSicon_vLRP2.svg
BSicon_BLc3.svg
BSicon_hLKRWl.svg
BSicon_HUBc3.svg
BSicon_kLLSTR2%2Br.svg
BSicon_HUB4f.svg
BSicon_eLABZq%2Bl.svg
BSicon_ldENDE@G.svg
BSicon_v-GRZ.svg
BSicon_uLSTRl.svg
BSicon_HUBtl.svg
BSicon_4HUBa@L.svg
BSicon_HUBtg-4.svg
BSicon_uexhkLLSTR2%2Br.svg
BSicon_dHUBe@gq.svg
BSicon_fLKRWr.svg
BSicon_fLSTR.svg
BSicon_gLLSTRl%2B4.svg
BSicon_LKRW%2Bl.svg
BSicon_uvLSHI2l-.svg
BSicon_uhLKRWl.svg
BSicon_uhkLLSTR3.svg
BSicon_MUSEUM.svg
BSicon_ldENDE@Fq.svg
BSicon_uhkLLSTR2.svg
BSicon_kHUBa@Fq.svg
BSicon_HUBsr-R.svg
BSicon_uexLSTRr%2B1.svg
BSicon_GRZ3%2Bl.svg
BSicon_WALK.svg
BSicon_dHUBtg-1.svg
BSicon_LLSTR%2B4.svg
BSicon_HUB-R.svg
BSicon_ldENDE@F.svg
BSicon_uexhkLLSTR%2B4.svg
BSicon_HUBc2.svg
BSicon_exhkLLSTR3%2Bl.svg
BSicon_LLSTR2%2B3.svg
BSicon_LLSTR2%2Br.svg
BSicon_LLSTR2%2B1.svg
BSicon_BLc4.svg
BSicon_kHUBa@F.svg
BSicon_lBHF_black.svg
BSicon_4HUBe@F~GGq.svg
BSicon_dGRZa.svg
BSicon_exhkLLSTRr%2B1.svg
BSicon_LLSTR3%2B4.svg
BSicon_HUBx-4.svg
BSicon_ANCHOR030.svg
BSicon_LRP4.svg
BSicon_lENDE@Fq-.svg
BSicon_uhkLLSTRc4.svg
BSicon_HUBe@g.svg
BSicon_exhkLLSTR%2B1.svg
BSicon_HUBe@g-Rq.svg
BSicon_exhkLLSTRc4.svg
BSicon_hkLLSTR2%2Br.svg
BSicon_exLLSTR3.svg
BSicon_GRZr%2Bg.svg
BSicon_cdHUBeq.svg
BSicon_uexLSTR3%2Bl.svg
BSicon_lENDE4.svg
BSicon_GRZr%2B1.svg
BSicon_uexhLSTR.svg
BSicon_exLKRWl.svg
BSicon_gLLSTR%2B1.svg
BSicon_uLABZglr.svg
BSicon_SUBWAY-CHN.svg
BSicon_exLSTR2%2B4.svg
BSicon_HUB%2Br-L.svg
BSicon_LLSTR2%2B4e.svg
BSicon_LKRWgl.svg
BSicon_exLLSTRl%2B4.svg
BSicon_hkLLSTR-c4.svg
BSicon_exLSTR3%2B1.svg
BSicon_exLABZr%2Br.svg
BSicon_exLLSTR2.svg
BSicon_cdSEP.svg
BSicon_uLABZg%2Blr.svg
BSicon_GRZ1m2.svg
BSicon_HUB-Lq.svg
BSicon_uLSTR3%2B1.svg
BSicon_uLABZr%2Br.svg
BSicon_exLSTR%2B4.svg
BSicon_HUBc1.svg
BSicon_ANCHOR.svg
BSicon_kHUBa@G.svg
BSicon_uLKRWgl.svg
BSicon_uLSTR2%2B4.svg
BSicon_4HUBa@L~RRq.svg
""".split('\n')))