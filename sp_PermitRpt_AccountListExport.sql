CREATE PROCEDURE [dbo].[sp_PermitRpt_AccountListExport]  
AS  
  
BEGIN  
  
 DECLARE @YearID SMALLINT = (SELECT YearID FROM dbo.xrYearColor WHERE IsCurrentFlag = 1);  
  
 SELECT   
  --TOP 10000  
   REPLACE(ParcelID,'-','') [ParcelID],  
   PropertyID  
  
 INTO 
	##temp_perm_rpt  
 FROM   
	Assess50.dbo.GetPropertiesTable(1,@YearID,1)  
 WHERE   
	1=1  
 AND  
	IsPersonalPropertyFlag = 0  
 AND   
	InactiveFlag = 0  
 AND  
	xrDistrictGroupID NOT IN (  
			SELECT xrDistrictGroupID FROM dbo.GetxrDistrictGroupTable(1,@YearID,1)  
			WHERE DistrictGroup IN ('1400','2200','3100','4300') 
			)  
 GROUP BY 
	REPLACE(ParcelID,'-',''), 
	PropertyID  
  
  
 CREATE CLUSTERED INDEX temp_perm_rpt_idx ON ##temp_perm_rpt (PropertyID ASC);  
  
  
 EXEC dbo.ext_ExportDataToCsv @dbName = N'tempdb',          -- nvarchar(100)  
         @includeHeaders = 0, -- bit  
         @filePath = N'\\network_folder\permit_reports',        -- nvarchar(512)  
         @tableName = N'##temp_perm_rpt',       -- nvarchar(100)  
         @reportName = N'Permit_Report_Account_List.txt',      -- nvarchar(100)  
         @delimiter = N'|'        -- nvarchar(4)  
  
 DROP TABLE IF EXISTS ##temp_perm_rpt  
  
  
END