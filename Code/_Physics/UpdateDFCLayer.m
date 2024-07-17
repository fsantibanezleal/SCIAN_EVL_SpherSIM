function layerDFC = UpdateDFCLayer( enviroment )

%% Update DFCs
    numDFCs = enviroment.embryoData.layerDFC.nDFCs;
    for indexDFC = 1:numDFCs
        layerDFC.cellDFC(indexDFC) = UpdateDFC(enviroment,indexDFC);
    end

end

