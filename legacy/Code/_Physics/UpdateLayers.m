function  updatedEnviroment = UpdateLayers(enviroment)

%% At this version EVLayer migrate on a independient way of DFCs 
% i.e. NO extrusion process considered yet
    %enviroment.layerEVL = updateEVLayer(enviroment);
%% Updating DFCLayer based on EVLayer, DFC-DFC interactions and external
% forces..
    enviroment.layerDFC = UpdateDFCLayer(enviroment);
%% Solve collisions with others Cells    
    enviroment.layerDFC = SolveCollidingDFCLayer(enviroment);
%% Global update    
    updatedEnviroment = enviroment;
end