[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "fabric_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared fabric = let
  Source = AzureStorage.Blobs("https://stadminaihub030337719738.blob.core.windows.net/"),
  #"Navigation 1" = Source{[Name = "fabric"]}[Data],
  Navigation = #"Navigation 1"{[#"Folder Path" = "https://stadminaihub030337719738.blob.core.windows.net/fabric/", Name = "dimension_customer.csv"]}[Content],
  #"Imported CSV" = Csv.Document(Navigation, [Delimiter = ",", Columns = 11, Encoding = 65001, QuoteStyle = QuoteStyle.None]),
  #"Promoted headers" = Table.PromoteHeaders(#"Imported CSV", [PromoteAllScalars = true]),
  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"CustomerKey", Int64.Type}, {"WWICustomerID", Int64.Type}, {"Customer", type text}, {"BillToCustomer", type text}, {"Category", type text}, {"BuyingGroup", type text}, {"PrimaryContact", type text}, {"PostalCode", type text}, {"ValidFrom", type datetime}, {"ValidTo", type datetime}, {"LineageKey", Int64.Type}})
in
  #"Changed column type";
shared fabric_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "33d534a2-dabe-4f41-a95b-f7819c2b0e69"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "74cb0798-e3da-4856-ab0e-9861e92c9a93"]}[Data],
  TableNavigation = Navigation_2{[Id = "DataflowGen2_dimension_customer", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
