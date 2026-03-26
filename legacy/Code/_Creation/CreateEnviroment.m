function enviroment = CreateEnviroment(embryoData)
%% Main function
    enviroment.embryoData = embryoData;
    
    enviroment.layerDFC   = CreateDFCLayer(embryoData);
    enviroment.layerEVL   = CreateEVLayer(embryoData);
    
end
