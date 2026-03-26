function layerDFC = CreateDFCLayer(embryoData)
%% Basic parameters
    % Mean radial size for initialize DFCs, in radians
    radialSize   = embryoData.layerDFC.radialSize;
    % Number of vertex for each DFC
    nVertexs     = embryoData.layerDFC.nVertexsDFC;
    % Radius for DFC Layer
    radiusLayer  = embryoData.embryo.radius;
    
    % Define available area for creation of DFC
    % For now... create to rows of DFCs
    minAzimuth       = embryoData.layerDFC.minAzimuth;
    maxAzimuth       = embryoData.layerDFC.maxAzimuth;    
    maxElevation     = embryoData.layerDFC.maxElevation;
    
    currentAzimuth   = minAzimuth + radialSize;
    currentElevation = maxElevation - radialSize;
    
%% Fill DFCs
    for indexDFC = 1:embryoData.layerDFC.nDFCs
        % Azimuth coordinate for current DFC
        centerAER(1)       = currentAzimuth;
        % Elevation coordinate for current DFC
        centerAER(2)       = currentElevation;
        % Radial coordinater for current DFC
        centerAER(3)       = radiusLayer;
        
        layerDFC.cellDFC(indexDFC) = CreateDFC(...
                                        centerAER,...
                                        radialSize,...
                                        nVertexs);
        
        % Update coordinates
        if currentAzimuth + 2.0*radialSize > maxAzimuth 
            currentAzimuth   = minAzimuth + radialSize;
            currentElevation = currentElevation - 2.0*radialSize;
        else
            currentAzimuth   = currentAzimuth + 2.0*radialSize;
        end
    end
end